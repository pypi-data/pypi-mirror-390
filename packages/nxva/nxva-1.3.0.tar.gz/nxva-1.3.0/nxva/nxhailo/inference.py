import os


class HefInference:
    import resource
    in_format, out_format = None, None
    interface, target, active_model_id, network_context, infer_pipeline = None, None, None, None, None
    models_pool = {}
    model_num = 0
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    os.environ["HAILORT_LOGGER_PATH"] = "NONE"
        
    def __init__(self, weight):
        self.load_model(weight)
       
    def load_model(self, weight):
        from hailo_platform import (
            VDevice, HEF, HailoStreamInterface, ConfigureParams,
            InputVStreamParams, OutputVStreamParams,
            FormatType
        )
        if HefInference.models_pool == {}:
            # Create a single VDevice
            HefInference.target = VDevice()
        try:
            self.model_id = HefInference.model_num
            HefInference.model_num += 1

            hef = HEF(weight)
            configure_params = ConfigureParams.create_from_hef(hef, interface=HailoStreamInterface.PCIe)
            network_group = HefInference.target.configure(hef, configure_params)[0]
            network_group_params = network_group.create_params()

            # vstream params
            input_vstreams_params = InputVStreamParams.make(network_group, format_type=FormatType.FLOAT32)
            output_vstreams_params = OutputVStreamParams.make(network_group, format_type=FormatType.FLOAT32)
            HefInference.models_pool[self.model_id] = {
                "hef": hef,
                "network_group": network_group,
                "network_group_params": network_group_params,
                "input_vstreams_params": input_vstreams_params,
                "output_vstreams_params": output_vstreams_params,
                "input_info": [n.name for n in hef.get_input_vstream_infos()],
                "output_infos": hef.get_output_vstream_infos(),
            }
        except Exception as e:
            HefInference.model_num -= 1
            raise ValueError(f"Error loading model {self.model_id}: {e}")

    def _activate_model(self):
        from hailo_platform import InferVStreams
        """Switch active model"""
        if hasattr(self, "network_context") and self.network_context is not None:
            HefInference.network_context.__exit__(None, None, None)
        if hasattr(self, "infer_pipeline") and self.infer_pipeline is not None:
            HefInference.infer_pipeline.__exit__(None, None, None)
        
        m = HefInference.models_pool[self.model_id]
        HefInference.network_context = m["network_group"].activate(m["network_group_params"])
        HefInference.infer_pipeline = InferVStreams(
            m["network_group"],
            m["input_vstreams_params"],
            m["output_vstreams_params"]
        )
        HefInference.network_context.__enter__()
        HefInference.infer_pipeline.__enter__()
        HefInference.active_model_id = self.model_id

    def switch_model(self):
        """Public method to switch model"""
        if self.model_id not in HefInference.models_pool:
            raise ValueError(f"Model {self.model_id} not found in pool")
        elif self.model_id == HefInference.active_model_id:
            return
        self._activate_model()

    def __call__(self, imgs):
        self.switch_model()
        m = HefInference.models_pool[HefInference.active_model_id]
        input_data = {m["input_info"][0]: imgs}
        results = HefInference.infer_pipeline.infer(input_data)
        return [results[info.name] for info in m["output_infos"]]

    def close(self):
        if hasattr(self, "infer_pipeline") and HefInference.infer_pipeline is not None:
            HefInference.infer_pipeline.__exit__(None, None, None)
        if hasattr(self, "network_context") and HefInference.network_context is not None:
            HefInference.network_context.__exit__(None, None, None)
        if hasattr(self, "target") and HefInference.target is not None:
            HefInference.target.release()