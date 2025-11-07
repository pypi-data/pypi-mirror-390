import numpy as np
import tensorrt as trt
import pycuda.driver as cuda

cuda.init()
_DEVICE = cuda.Device(0)
_PRIMARY_CTX = _DEVICE.retain_primary_context()

class TRTInference:
    def __init__(self, engine_path, input_shape):
        """
        初始化 TRTWrapper，載入 TensorRT Engine，並準備執行所需的 CUDA 資源與記憶體配置。

        Args:
            engine_path (str):
                TensorRT engine 檔案的路徑（例如 'model.engine'）。
            input_shape (List[Tuple[int]]):
                模型每個輸入的 shape 組成的列表，例如 [(1, 3, 640, 640)]。
                對於多輸入模型，這裡需要列出每個 input tensor 的 shape。
        """
        self.TRT_LOGGER = trt.Logger()
        self.ctx = _PRIMARY_CTX
        self.ctx.push()
        try:
            with open(engine_path, "rb") as f:
                self.runtime = trt.Runtime(self.TRT_LOGGER)
                self.engine = self.runtime.deserialize_cuda_engine(f.read())

            self.context = self.engine.create_execution_context()

            # 版本判斷：8.5 以上使用 v3 API
            major_version, minor_version, *_ = map(int, trt.__version__.split('.'))
            self.use_v3 = (major_version, minor_version) >= (8, 5)

            # 使用者提供之參考輸入 shape（靜態引擎時會用到）
            assert isinstance(input_shape, list), "input_shape should be list, e.g. [(B,C,H,W)]"
            assert all(isinstance(s, tuple) for s in input_shape), "input_shape elements must be tuple"
            self.input_shapes = input_shape

            # 名稱與 dtype
            self.input_names = []
            self.output_names = []
            self.input_dtypes = []
            self.output_dtypes = []

            if self.use_v3:
                for idx in range(self.engine.num_io_tensors):
                    name = self.engine.get_tensor_name(idx)
                    mode = self.engine.get_tensor_mode(name)
                    if mode == trt.TensorIOMode.INPUT:
                        self.input_names.append(name)
                        self.input_dtypes.append(self.engine.get_tensor_dtype(name))
                    else:
                        self.output_names.append(name)
                        self.output_dtypes.append(self.engine.get_tensor_dtype(name))
                # dynamic 判定（v3 用名字取 shape）
                self.is_dynamic = any(-1 in self.engine.get_tensor_shape(n) for n in self.input_names)
            else:
                # v2/fallback：沿用舊式 binding index 方式
                self.input_bindings = []
                self.output_bindings = []
                for i in range(self.engine.num_bindings):
                    name = self.engine.get_binding_name(i)
                    if self.engine.binding_is_input(i):
                        self.input_names.append(name)
                        self.input_dtypes.append(self.engine.get_binding_dtype(i))
                        self.input_bindings.append(i)
                    else:
                        self.output_names.append(name)
                        self.output_dtypes.append(self.engine.get_binding_dtype(i))
                        self.output_bindings.append(i)
                self.is_dynamic = any(-1 in self.engine.get_binding_shape(i) for i in self.input_bindings)

            # 共用緩衝池（名稱 -> device allocation）
            self._bufs = {}
            self._buf_bytes = {}

            # 靜態引擎：預先配好 input/output 的顯存（依 engine 固定 shape）
            self.d_inputs = []
            self.d_outputs = []
            self.output_shapes = []

            if not self.is_dynamic:
                # 預配輸入
                for shape, dtype in zip(self.input_shapes, self.input_dtypes):
                    np_dtype = np.float16 if dtype == trt.DataType.HALF else np.float32
                    self.d_inputs.append(cuda.mem_alloc(int(np.prod(shape)) * np.dtype(np_dtype).itemsize))

                # 預配輸出（用 engine 的固定 shape）
                if self.use_v3:
                    for name, dtype in zip(self.output_names, self.output_dtypes):
                        np_dtype = np.float16 if dtype == trt.DataType.HALF else np.float32
                        oshape = tuple(self.engine.get_tensor_shape(name))
                        self.output_shapes.append(oshape)
                        self.d_outputs.append(cuda.mem_alloc(int(np.prod(oshape)) * np.dtype(np_dtype).itemsize))
                else:
                    for i, dtype in zip(self.output_bindings, self.output_dtypes):
                        np_dtype = np.float16 if dtype == trt.DataType.HALF else np.float32
                        oshape = tuple(self.engine.get_binding_shape(i))
                        self.output_shapes.append(oshape)
                        self.d_outputs.append(cuda.mem_alloc(int(np.prod(oshape)) * np.dtype(np_dtype).itemsize))

            # 單一長駐 stream（v2/v3 皆可用 async 複製與執行）
            self.stream = cuda.Stream()

        finally:
            self.ctx.pop()

    def infer(self, input_array):
        """
        進行推論（8.5+ 走 v3 API，否則走 v2）。
        input_array: List[np.ndarray]，每個元素對應一個輸入 tensor。
        """
        self.ctx.push()
        try:
            assert isinstance(input_array, list) and all(isinstance(a, np.ndarray) for a in input_array)

            if self.use_v3 and hasattr(self.context, "execute_async_v3"):
                # ----------- V3 路徑（Tensor 名稱 + set_tensor_address）-----------
                # 設定輸入 shape 並 HtoD
                for name, arr, dtype in zip(self.input_names, input_array, self.input_dtypes):
                    if arr.ndim == 3:
                        arr = np.expand_dims(arr, axis=0)
                    self.context.set_input_shape(name, tuple(arr.shape))

                    np_dtype = np.float16 if dtype == trt.DataType.HALF else np.float32
                    arr = np.ascontiguousarray(arr.astype(np_dtype))

                    d_input = self._get_buf(name, arr.nbytes)  # 動態形狀：按需擴張/重用
                    cuda.memcpy_htod_async(d_input, arr, self.stream)
                    # 重要：設定對應的 device address
                    self.context.set_tensor_address(name, int(d_input))

                # 配置輸出緩衝（依目前實際 shape）
                for name, dtype in zip(self.output_names, self.output_dtypes):
                    oshape = tuple(self.context.get_tensor_shape(name))
                    np_dtype = np.float16 if dtype == trt.DataType.HALF else np.float32
                    nbytes = int(np.prod(oshape)) * np.dtype(np_dtype).itemsize
                    d_output = self._get_buf(name, nbytes)
                    self.context.set_tensor_address(name, int(d_output))

                # 執行
                self.context.execute_async_v3(self.stream.handle)

                # 取回輸出
                outputs = []
                for name, dtype in zip(self.output_names, self.output_dtypes):
                    oshape = tuple(self.context.get_tensor_shape(name))
                    np_dtype = np.float16 if dtype == trt.DataType.HALF else np.float32
                    out_host = np.empty(oshape, dtype=np_dtype)
                    cuda.memcpy_dtoh_async(out_host, self._bufs[name], self.stream)
                    outputs.append(out_host)

                # 等待所有 async 完成
                self.stream.synchronize()
                return outputs

            else:
                # ----------- V2 路徑（舊式 bindings + execute_async_v2）-----------
                bindings = [0] * self.engine.num_bindings

                if self.is_dynamic:
                    d_inputs = []
                    d_outputs = []
                    output_shapes = []

                    # 設 shape + HtoD
                    for name, arr, dtype, i in zip(self.input_names, input_array, self.input_dtypes, self.input_bindings):
                        if arr.ndim == 3:
                            arr = np.expand_dims(arr, axis=0)
                        np_dtype = np.float16 if dtype == trt.DataType.HALF else np.float32
                        arr = np.ascontiguousarray(arr.astype(np_dtype))
                        self.context.set_binding_shape(i, tuple(arr.shape))
                        d_input = self._get_buf(name, arr.nbytes)
                        cuda.memcpy_htod_async(d_input, arr, self.stream)
                        d_inputs.append(d_input)
                        bindings[i] = int(d_input)

                    # 配輸出
                    for name, i, dtype in zip(self.output_names, self.output_bindings, self.output_dtypes):
                        oshape = tuple(self.context.get_binding_shape(i))
                        output_shapes.append(oshape)
                        np_dtype = np.float16 if dtype == trt.DataType.HALF else np.float32
                        nbytes = int(np.prod(oshape)) * np.dtype(np_dtype).itemsize
                        d_output = self._get_buf(name, nbytes)
                        d_outputs.append(d_output)
                        bindings[i] = int(d_output)

                    # 執行
                    self.context.execute_async_v2(bindings, self.stream.handle)

                    # DtoH
                    outputs = []
                    for oshape, d_out, dtype in zip(output_shapes, d_outputs, self.output_dtypes):
                        np_dtype = np.float16 if dtype == trt.DataType.HALF else np.float32
                        out_host = np.empty(oshape, dtype=np_dtype)
                        cuda.memcpy_dtoh_async(out_host, d_out, self.stream)
                        outputs.append(out_host)
                    self.stream.synchronize()
                    return outputs

                else:
                    # 靜態：直接用預配的 d_inputs/d_outputs
                    # 設定 shape（v2 需 set_binding_shape；v3 不會走到這）
                    for arr, d_input, i, dtype in zip(input_array, self.d_inputs, self.input_bindings, self.input_dtypes):
                        if arr.ndim == 3:
                            arr = np.expand_dims(arr, axis=0)
                        np_dtype = np.float16 if dtype == trt.DataType.HALF else np.float32
                        arr = np.ascontiguousarray(arr.astype(np_dtype))
                        self.context.set_binding_shape(i, tuple(arr.shape))
                        cuda.memcpy_htod_async(d_input, arr, self.stream)
                        bindings[i] = int(d_input)

                    for d_output, i in zip(self.d_outputs, self.output_bindings):
                        bindings[i] = int(d_output)

                    self.context.execute_async_v2(bindings, self.stream.handle)

                    outputs = []
                    for shape, d_out, dtype in zip(self.output_shapes, self.d_outputs, self.output_dtypes):
                        np_dtype = np.float16 if dtype == trt.DataType.HALF else np.float32
                        out_host = np.empty(shape, dtype=np_dtype)
                        cuda.memcpy_dtoh_async(out_host, d_out, self.stream)
                        outputs.append(out_host)
                    self.stream.synchronize()
                    return outputs

        finally:
            self.ctx.pop()

    def _get_buf(self, name, nbytes):
        cur = self._buf_bytes.get(name, 0)
        if cur < nbytes:
            old = self._bufs.get(name)
            if old is not None:
                try: old.free()
                except Exception: pass
            self._bufs[name] = cuda.mem_alloc(nbytes)
            self._buf_bytes[name] = nbytes
        return self._bufs[name]
