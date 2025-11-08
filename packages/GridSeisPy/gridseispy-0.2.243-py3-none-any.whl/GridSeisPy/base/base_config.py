import typing
from .base_class import CVDFile


class FromClsNode:
    """必须从类中获取参数的节点
    由于时间原因，还没有写
    """


class BaseConfig(CVDFile):
    """
    必设参数: 类型注解不为None, 且参数值为None
    配置参数要求: 1. 配置参数必须有类型注解, 2. 配置参数必须有默认值, 3. 配置参数可以通过typing.Annotated添加描述(类型注解在最前面, 描述在后面)
    配置基类，用于存储配置参数，要求配置参数必须有类型注解，否则无类型注解变量无法被转换为字典
    并提供to_dict和from_dict方法，用于将配置参数转换为字典和从字典转换为配置参数
    """

    # def __getstate__(self):
    #     """自定义序列化，保存实例属性及类属性"""
    #     # # 只负责类属性
    #     # state = type(self).__dict__.copy()
    #     # return state

    #     # 保存实例属性及类属性
    #     state = self.__dict__.copy()  # 保存实例属性
    #     # 将类属性作为特殊键添加到 state
    #     cls = type(self)
    #     for key, value in cls.__dict__.items():
    #         state[f'_class_{key}'] = value
    #     return state
    
    # def __setstate__(self, state):
    #     """自定义反序列化，恢复实例属性及类属性"""
    #     # 只负责类属性
    #     # state = state.update({k: v for k, v in state.items() if not k.startswith('_class_')})
    #     # return state

    #     # 先恢复实例属性
    #     self.__dict__.update({k: v for k, v in state.items() if not k.startswith('_class_')})
    #     # 恢复类属性
    #     cls = type(self)
    #     for key, value in state.items():
    #         if key.startswith('_class_'):
    #             setattr(cls, key[7:], value)
    #     return cls()

    def to_dict(self) -> dict:
        # 使用 __annotations__ 只获取有类型注解的类变量，并过滤掉可调用对象（如方法）
        cls = type(self)
        dict_config = {
            key: getattr(self, key) for key, value in cls.__dict__.items() 
            if key in cls.__annotations__ and not callable(value)
            }
        return dict_config

    @classmethod
    def to_desc(cls) -> dict:
        # cls_name = cls.__qualname__.split('.')[0]
        cls_name = cls.__qualname__
        # 从 __qualname__ 解析出外部类名（如 'UNet3D_Simple.cfg' -> 'UNet3D_Simple'）
        desc_dict = {}
        for key, annotations in cls.__annotations__.items():
            if annotations is callable: continue
            annotations, *desc = typing.get_args(annotations) if typing.get_origin(annotations) == typing.Annotated else (annotations, '')
            
            type_str = annotations.__name__ if type(annotations) == type(type(None)) else str(annotations)
            if 'None' not in type_str and  getattr(cls, key) is None:  # 处理必设参数(类型注解不为None, 且参数值为None)
                desc = ['必设参数, 配置参数时不能为空'] + desc
            desc_dict[key] = {'type': type_str , 'default': getattr(cls, key) if hasattr(cls, key) else None, 'description': desc}
        return desc_dict
    
    @classmethod
    def from_dict(cls, dict_config: dict, ) -> 'BaseConfig':
        """ 
        从字典中, 更新配置参数, 并返回新的配置参数类
        配置参数要求: 1. 配置参数必须有类型注解, 2. 配置参数必须有默认值, 3. 配置参数必须有描述
        :param dict_config: 配置参数字典
        :return: 新的配置参数类
        """
        # cls_name = cls.__qualname__.split('.')[0]
        self = cls()
        cls_name = cls.__qualname__
        # 从 __qualname__ 解析出外部类名（如 'UNet3D_Simple.cfg' -> 'UNet3D_Simple'）
        for key, value in dict_config.items():
            try: annotations = cls.__annotations__[key]
            except KeyError: raise KeyError(f"配置参数时, {cls_name}的 '{key}' 参数不存在, 请重新配置参数")
            # assert (value is not None) or annotations is None, f"配置参数时, {cls_name}的 '{key}' 参数值不能为空, 请重新配置参数"
            origin_type = typing.get_origin(annotations)
            except_type = annotations if origin_type is None else origin_type
            if except_type == typing.Annotated: # 处理注解类型
                annotations, *desc = typing.get_args(annotations)
                origin_type = typing.get_origin(annotations)
                except_type = annotations if origin_type is None else origin_type

            if except_type == type(int | str) or except_type == typing.Union: # 处理联合类型
                union_types = typing.get_args(annotations)
                if type(value) not in union_types:
                    assert False, f"配置参数时, {cls_name}的 '{key}' 参数类型不匹配, 期望参数类型: {union_types}, 实际参数类型: {type(value)}, 请重新配置参数"
                except_type = type(value)
            
            if except_type == FromClsNode: # 处理从类中获取参数的节点, 该类型直接获取
                except_type = type(value)
                
            except_type = type(None) if except_type is None else except_type
            assert except_type != callable, f"配置参数时, {cls_name}的 '{key}' 参数类型应为{type(callable)}, 实际参数类型: {type(value)}, 请重新配置参数"
            assert isinstance(value, except_type), f"配置参数时, {cls_name}的 '{key}' 参数类型不匹配, 期望参数类型: {except_type}, 实际参数类型: {type(value)}, 请重新配置参数"
            setattr(self, key, value)   # 已优化，不需要单独设置__setstate__和__getstate__了。
        return self



# from typing import Annotated, Optional, Tuple
# class DefaultConfig(BaseConfig):
#         # 基础训练流程参数
#         max_epochs: Annotated[int, '最大训练轮数'] = 1
#         learning_rate: Annotated[float, '学习率'] = 1e-3

#         # 数据标准化参数
#         scaler_mean: Annotated[Optional[float], '数据标准化均值'] = 1.0
#         scaler_std: Annotated[Optional[float], '数据标准化标准差'] = 1.0

#         # 平滑性损失参数
#         smoothness_weight: Annotated[float, '平滑性损失权重'] = 0.01
#         no_label_smoothness_weight: Annotated[float, '无标签平滑性损失权重'] = 0.1
#         smoothness_type: Annotated[str, '平滑性损失类型'] = 'anisotropic_l2'
#         smoothness_enabled: Annotated[bool, '是否启用平滑性损失'] = True
#         aniso_weight_vertical: Annotated[float, '垂直方向各向异性权重'] = 0.3
#         aniso_weight_inline: Annotated[float, 'inline方向各向异性权重'] = 1.0
#         aniso_weight_crossline: Annotated[float, 'crossline方向各向异性权重'] = 1.0

#         # 语义一致性参数
#         semantic_weight: Annotated[float, '语义一致性损失权重'] = 0.01
#         semantic_enabled: Annotated[bool, '是否启用语义一致性损失'] = True
#         semantic_embed_dim: Annotated[int, '语义编码器嵌入维度'] = 256
#         semantic_proj_dim: Annotated[int, '语义投影维度'] = 128

#         # 优化器配置参数
#         discriminator_lr_ratio: Annotated[float, '判别器学习率比例'] = 0.5
#         weight_decay: Annotated[float, '权重衰减'] = 1e-5
#         optimizer_betas: Annotated[Tuple[float, float], 'Adam优化器beta参数'] = (0.9, 0.999)

#         # 语义损失训练配置参数
#         semantic_trace_sample_ratio: Annotated[float, '语义道采样比例'] = 0.1
#         semantic_warmup_epochs: Annotated[int, '语义损失warmup轮数'] = 0
#         semantic_use_global_batch: Annotated[bool, '语义对比是否使用全局批（跨卡 all_gather），默认 True。'] = True
# CVDFile.SetVDPath()
# # print(type(None) != type(None), typing.get_origin(None))
# a = DefaultConfig.from_dict({
#     "aniso_weight_inline": 250.0,
#     "aniso_weight_crossline": 1.000001
#   })
# c = a.to_dict()
# d = a.to_desc()
# a = DefaultConfig.from_dict(c)
# print(d)
# a.Update2VDFile('test_config')
# b = DefaultConfig.GetObjByName('test_config')
# c = DefaultConfig()
# b.to_dict()
