import inspect
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Generic,
    TypeVar,
    cast,
    overload,
)
from typing_extensions import Self

from pydantic import (
    ConfigDict,
    computed_field,
)
from sqlalchemy.orm import column_property, declared_attr
from sqlmodel import JSON, Column, Computed, Field, Integer, Relationship

from ._utils import move_to_last
from .build_model import (
    BaseGeneralModel,
    BaseResModel,
    BaseResModelWithOptionalId,
    ConvertToORM,
)

if TYPE_CHECKING:
    from .effect import PetEffectORM, VariationEffectORM
    from .items import (
        EnergyBeadORM,
        EquipBonusORM,
        GemORM,
        SkillStoneEffectORM,
        SuitBonusORM,
    )
    from .pet import SoulmarkORM
    from .skill import SkillEffectType, SkillEffectTypeORM, SkillORM


TResModel = TypeVar('TResModel', bound=BaseResModel)
_TResModelArg = TypeVar('_TResModelArg', bound=BaseResModel)


class ResourceRef(BaseGeneralModel, Generic[TResModel]):
    """API资源类"""

    base_data_url: ClassVar[str] = ''

    id: int = Field(description='资源ID')
    resource_name: str = Field(description='资源类型名称', exclude=True)
    path: str = Field(default='', description='资源路径', exclude=True)

    @computed_field(description='资源URL')
    @property
    def url(self) -> str:
        path_parts: list[str] = [
            self.base_data_url,
            self.resource_name,
            str(self.id),
            self.path,
        ]
        return '/'.join(path_parts)

    @classmethod
    def schema_path(cls) -> str:
        return 'common/resource_ref/'

    @overload
    @classmethod
    def from_model(
        cls,
        model: _TResModelArg,
        *,
        resource_name: str | None = None,
    ) -> 'ResourceRef[_TResModelArg]': ...

    @overload
    @classmethod
    def from_model(
        cls,
        model: type[_TResModelArg],
        *,
        id: int,
        resource_name: str | None = None,
    ) -> 'ResourceRef[_TResModelArg]': ...

    @classmethod
    def from_model(
        cls,
        model: type[_TResModelArg] | _TResModelArg,
        *,
        id: int | None = None,
        resource_name: str | None = None,
    ) -> 'ResourceRef[_TResModelArg]':
        if not inspect.isclass(model):
            id = model.id
        if id is None:
            raise ValueError('id is required')

        resource_name = resource_name or model.resource_name()
        obj = cls(id=id, resource_name=resource_name)
        return cast(ResourceRef[_TResModelArg], obj)


class NamedResourceRef(ResourceRef[TResModel]):
    name: str | None = Field(default=None, description='资源名称')

    @classmethod
    def schema_path(cls) -> str:
        return 'common/named_resource_ref/'


class ApiResourceList(BaseGeneralModel, Generic[TResModel]):
    """API资源列表，兼容RFC 5988的Link标准"""

    count: int = Field(description='资源数量')
    next: str | None = Field(default=None, description='下一页URL')
    previous: str | None = Field(default=None, description='上一页URL')
    first: str | None = Field(default=None, description='第一页URL')
    last: str | None = Field(default=None, description='最后一页URL')
    results: list[NamedResourceRef[TResModel]] = Field(description='资源列表')

    @classmethod
    def schema_path(cls) -> str:
        return 'common/api_resource_list/'


class EidEffect(BaseResModel, BaseGeneralModel, ConvertToORM['EidEffectORM']):
    # info: str | None = Field(
    #     default=None,
    #     description='效果描述，当效果描述为空时，该字段为null',
    # )
    args_num: int = Field(
        description='效果需要的参数数量，该值是从使用该效果的资源中推测得出的'
    )

    @classmethod
    def schema_path(cls) -> str:
        return 'common/eid_effect/'

    @classmethod
    def resource_name(cls) -> str:
        return 'eid_effect'

    @classmethod
    def get_orm_model(cls) -> type['EidEffectORM']:
        return EidEffectORM

    def to_orm(self) -> 'EidEffectORM':
        return EidEffectORM(id=self.id, args_num=self.args_num)


class EidEffectORM(EidEffect, table=True):
    in_use: list['EidEffectInUseORM'] = Relationship(back_populates='effect')


class EidEffectInUseBase(BaseResModelWithOptionalId):
    effect_args: list[int] | None = Field(
        default=None,
        description='效果参数，当效果参数为空时，该字段为null',
        sa_type=JSON,
    )

    @classmethod
    def resource_name(cls) -> str:
        return 'eid_effect_in_use'


class EidEffectInUse(
    EidEffectInUseBase, BaseGeneralModel, ConvertToORM['EidEffectInUseORM']
):
    effect: 'ResourceRef[EidEffect]' = Field(description='效果引用')

    @classmethod
    def schema_path(cls) -> str:
        return 'common/eid_effect_in_use/'

    @classmethod
    def get_orm_model(cls) -> type['EidEffectInUseORM']:
        return EidEffectInUseORM

    def to_orm(self) -> 'EidEffectInUseORM':
        return EidEffectInUseORM(
            id=self.id,
            eid=self.effect.id,
            effect_args=self.effect_args,
        )


class EidEffectInUseORM(EidEffectInUseBase, table=True):
    eid: int = Field(foreign_key='eid_effect.id')
    effect: 'EidEffectORM' = Relationship(back_populates='in_use')
    # 特性，魂印，装备效果，etc...
    energy_bead: 'EnergyBeadORM' = Relationship(back_populates='effect_in_use')
    soulmark: 'SoulmarkORM' = Relationship(back_populates='effect_in_use')
    pet_effect: 'PetEffectORM' = Relationship(back_populates='effect_in_use')
    variation_effect: 'VariationEffectORM' = Relationship(
        back_populates='effect_in_use'
    )
    equip_bonus: 'EquipBonusORM' = Relationship(back_populates='effect_in_use')
    suit_bonus: 'SuitBonusORM' = Relationship(back_populates='effect_in_use')


class SixAttributesBase(BaseResModelWithOptionalId, BaseGeneralModel):
    """六维属性类"""

    atk: int = Field(description='攻击')
    def_: int = Field(
        sa_type=Integer,
        sa_column_kwargs={'name': 'def', 'nullable': False},
        description='防御',
        schema_extra={'serialization_alias': 'def'},
    )
    sp_atk: int = Field(description='特攻')
    sp_def: int = Field(description='特防')
    spd: int = Field(description='速度')
    hp: int = Field(description='体力')

    percent: bool = Field(
        default=False,
        description='该对象描述的是否是百分比加成，如果为true，属性值为省略百分比（%）符号的加成',
    )

    @classmethod
    def schema_path(cls) -> str:
        return 'common/six_attributes/'

    @classmethod
    def from_string(
        cls, value: str, *, hp_first: bool = False, percent: bool = False
    ) -> Self:
        """从字符串创建六维属性对象"""
        attributes = value.split(' ')
        if len(attributes) < 6:
            raise ValueError('无效的属性字符串')
        attributes = [int(attribute) for attribute in attributes[0:6]]
        return cls.from_list(attributes, hp_first=hp_first, percent=percent)

    @classmethod
    def from_list(
        cls, attributes: list[int], *, hp_first: bool = False, percent: bool = False
    ) -> Self:
        if len(attributes) < 6:
            raise ValueError('无效的属性列表')
        if hp_first:
            move_to_last(attributes, 0)
        return cls(
            atk=attributes[0],
            def_=attributes[1],
            sp_atk=attributes[2],
            sp_def=attributes[3],
            spd=attributes[4],
            hp=attributes[5],
            percent=percent,
        )

    def __add__(self, other) -> Self:
        """两个六维属性相加"""
        cls = type(self)
        if not isinstance(other, cls):
            return self
        return cls(
            atk=self.atk + other.atk,
            def_=self.def_ + other.def_,
            sp_atk=self.sp_atk + other.sp_atk,
            sp_def=self.sp_def + other.sp_def,
            spd=self.spd + other.spd,
            hp=self.hp + other.hp,
        )

    def __sub__(self, other) -> Self:
        """两个六维属性相减"""
        cls = type(self)
        if not isinstance(other, cls):
            return self
        return cls(
            atk=self.atk - other.atk,
            def_=self.def_ - other.def_,
            sp_atk=self.sp_atk - other.sp_atk,
            sp_def=self.sp_def - other.sp_def,
            spd=self.spd - other.spd,
            hp=self.hp - other.hp,
        )

    @classmethod
    def resource_name(cls) -> str:
        return 'six_attributes'


class SixAttributes(
    SixAttributesBase, BaseGeneralModel, ConvertToORM['SixAttributesORM']
):
    @computed_field
    @property
    def total(self) -> int:
        """总属性值"""
        return self.atk + self.def_ + self.sp_atk + self.sp_def + self.spd + self.hp

    @classmethod
    def get_orm_model(cls) -> type['SixAttributesORM']:
        return SixAttributesORM

    def to_orm(self) -> 'SixAttributesORM':
        return SixAttributesORM(
            atk=self.atk,
            def_=self.def_,
            sp_atk=self.sp_atk,
            sp_def=self.sp_def,
            spd=self.spd,
            hp=self.hp,
            percent=self.percent,
        )


class SixAttributesORM(SixAttributesBase):
    model_config = ConfigDict(ignored_types=(declared_attr,))  # type: ignore

    @declared_attr
    def total(self):  # type: ignore
        return column_property(
            Column(
                Integer,
                Computed('atk + def + sp_atk + sp_def + spd + hp'),
                nullable=False,
            )
        )


class SkillEffectInUseBase(BaseResModelWithOptionalId):
    """描述一条“使用中的”技能效果"""

    info: str = Field(description='技能效果描述')
    args: list[int | float] | list[int] | list[float] = Field(
        description='技能效果参数列表',
        sa_type=JSON,
    )

    @classmethod
    def resource_name(cls) -> str:
        return 'skill_effect_in_use'


class SkillEffectInUse(
    SkillEffectInUseBase, BaseGeneralModel, ConvertToORM['SkillEffectInUseORM']
):
    effect: 'ResourceRef[SkillEffectType]'

    @classmethod
    def schema_path(cls) -> str:
        return 'common/skill_effect_in_use/'

    @classmethod
    def get_orm_model(cls) -> type['SkillEffectInUseORM']:
        return SkillEffectInUseORM

    def to_orm(self) -> 'SkillEffectInUseORM':
        return SkillEffectInUseORM(
            effect_id=self.effect.id,
            args=self.args,
            info=self.info,
        )


class SkillEffectInUseORM(SkillEffectInUseBase, table=True):
    effect_id: int = Field(foreign_key='skill_effect_type.id')
    effect: 'SkillEffectTypeORM' = Relationship(back_populates='in_use')
    skill: list['SkillORM'] = Relationship(
        sa_relationship_kwargs={
            'secondary': 'skilleffectlink',
        }
    )
    friend_skill: list['SkillORM'] = Relationship(
        sa_relationship_kwargs={
            'secondary': 'skillfriendskilleffectlink',
        }
    )
    gem: list['GemORM'] = Relationship(
        back_populates='skill_effect_in_use',
        sa_relationship_kwargs={
            'secondary': 'gemeffectlink',
        },
    )
    skill_stone_effect: list['SkillStoneEffectORM'] = Relationship(
        back_populates='effect',
        sa_relationship_kwargs={
            'secondary': 'skillstoneeffectlink',
        },
    )


__all__ = [
    'ApiResourceList',
    'EidEffect',
    'EidEffectInUse',
    'EidEffectInUseBase',
    'EidEffectInUseORM',
    'EidEffectORM',
    'NamedResourceRef',
    'ResourceRef',
    'SixAttributes',
    'SixAttributesBase',
    'SixAttributesORM',
    'SkillEffectInUse',
    'SkillEffectInUseBase',
    'SkillEffectInUseORM',
]
