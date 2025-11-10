from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from seerapi_models.build_model import (
    BaseCategoryModel,
    BaseResModel,
    BaseResModelWithOptionalId,
    ConvertToORM,
)
from seerapi_models.common import ResourceRef, SkillEffectInUse, SkillEffectInUseORM

from ._common import Item, ItemORM

if TYPE_CHECKING:
    from ..element_type import TypeCombination, TypeCombinationORM


class SkillStoneEffectLink(SQLModel, table=True):
    """技能石效果链接表"""

    skill_stone_effect_id: int | None = Field(
        default=None, foreign_key='skill_stone_effect.id', primary_key=True
    )
    effect_in_use_id: int | None = Field(
        default=None, foreign_key='skill_effect_in_use.id', primary_key=True
    )


class SkillStoneEffectBase(BaseResModelWithOptionalId):
    prob: float = Field(description='技能石效果激活概率，0到1之间')
    skill_stone_id: int = Field(
        description='技能石ID', foreign_key='skill_stone.id', exclude=True
    )

    @classmethod
    def resource_name(cls) -> str:
        return 'skill_stone_effect'


class SkillStoneEffect(SkillStoneEffectBase, ConvertToORM['SkillStoneEffectORM']):
    effect: list['SkillEffectInUse'] = Field(description='技能石效果列表')

    @classmethod
    def get_orm_model(cls) -> type['SkillStoneEffectORM']:
        return SkillStoneEffectORM

    def to_orm(self) -> 'SkillStoneEffectORM':
        return SkillStoneEffectORM(
            id=self.id,
            prob=self.prob,
            skill_stone_id=self.skill_stone_id,
            effect=[effect.to_orm() for effect in self.effect],
        )


class SkillStoneEffectORM(SkillStoneEffectBase, table=True):
    effect: list['SkillEffectInUseORM'] = Relationship(
        back_populates='skill_stone_effect',
        link_model=SkillStoneEffectLink,
    )
    skill_stone: 'SkillStoneORM' = Relationship(back_populates='effect')


class SkillStoneBase(BaseResModel):
    id: int = Field(primary_key=True, foreign_key='item.id', description='技能石ID')
    name: str = Field(description='技能石名称')
    rank: int = Field(description='技能石等级，1到5分别对应D, C, B, A, S')
    power: int = Field(description='技能石威力')
    max_pp: int = Field(description='技能石最大PP')
    accuracy: int = Field(description='技能石命中率')

    @classmethod
    def resource_name(cls) -> str:
        return 'skill_stone'


class SkillStone(SkillStoneBase, ConvertToORM['SkillStoneORM']):
    category: ResourceRef['SkillStoneCategory'] = Field(description='技能石分类')
    item: ResourceRef['Item'] = Field(description='技能石物品资源引用')
    effect: list['SkillStoneEffect'] = Field(description='完美技能石效果列表')

    @classmethod
    def get_orm_model(cls) -> type['SkillStoneORM']:
        return SkillStoneORM

    def to_orm(self) -> 'SkillStoneORM':
        return SkillStoneORM(
            id=self.id,
            name=self.name,
            rank=self.rank,
            power=self.power,
            max_pp=self.max_pp,
            accuracy=self.accuracy,
            category_id=self.category.id,
        )


class SkillStoneORM(SkillStoneBase, table=True):
    category_id: int = Field(
        description='技能石分类ID', foreign_key='skill_stone_category.id'
    )
    category: 'SkillStoneCategoryORM' = Relationship(
        back_populates='skill_stone',
    )
    item: 'ItemORM' = Relationship(
        back_populates='skill_stone',
    )
    effect: list['SkillStoneEffectORM'] = Relationship(
        back_populates='skill_stone',
    )


class SkillStoneCategoryBase(BaseCategoryModel):
    name: str = Field(description='技能石分类名称')

    @classmethod
    def resource_name(cls) -> str:
        return 'skill_stone_category'


class SkillStoneCategory(SkillStoneCategoryBase, ConvertToORM['SkillStoneCategoryORM']):
    skill_stone: list[ResourceRef['SkillStone']] = Field(
        default_factory=list,
        description='技能石列表',
    )
    type: ResourceRef['TypeCombination'] = Field(description='技能石类型')

    @classmethod
    def get_orm_model(cls) -> 'type[SkillStoneCategoryORM]':
        return SkillStoneCategoryORM

    def to_orm(self) -> 'SkillStoneCategoryORM':
        return SkillStoneCategoryORM(
            id=self.id,
            name=self.name,
            type_id=self.type.id,
        )


class SkillStoneCategoryORM(SkillStoneCategoryBase, table=True):
    type_id: int = Field(
        description='技能石类型ID', foreign_key='element_type_combination.id'
    )
    type: 'TypeCombinationORM' = Relationship(
        back_populates='skill_stone_category',
    )
    skill_stone: list['SkillStoneORM'] = Relationship(
        back_populates='category',
    )
