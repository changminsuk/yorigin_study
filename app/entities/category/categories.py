import dataclasses

from app.entities.category.category_codes import CategoryCode


@dataclasses.dataclass
class Category:
    code: str
    name: str
    image_url: str
    deep_link: str


CATEGORIES: dict[CategoryCode, Category] = {
    CategoryCode.CHICKEN: Category(
        code=CategoryCode.CHICKEN, name="치킨", image_url="https://chicken.png", deep_link="app://chicken_action"
    ),
    CategoryCode.BURGER: Category(
        code=CategoryCode.BURGER, name="버거", image_url="https://burger.png", deep_link="app://burger_action"
    ),
    CategoryCode.PIZZA: Category(
        code=CategoryCode.PIZZA, name="피자", image_url="https://pizza.png", deep_link="app://pizza_action"
    ),
    CategoryCode.SANDWICH: Category(
        code=CategoryCode.SANDWICH, name="샌드위치", image_url="https://sandwich.png", deep_link="app://sandwich_action"
    ),
    CategoryCode.KOREAN: Category(
        code=CategoryCode.KOREAN, name="한식", image_url="https://korean.png", deep_link="app://korean_action"
    ),
    CategoryCode.JAPANESE: Category(
        code=CategoryCode.JAPANESE, name="일식", image_url="https://japanese.png", deep_link="app://japanese_action"
    ),
    CategoryCode.SALAD: Category(
        code=CategoryCode.SALAD, name="샐러드", image_url="https://salad.png", deep_link="app://salad_action"
    ),
    CategoryCode.CAFE: Category(
        code=CategoryCode.CAFE, name="카페", image_url="https://cafe.png", deep_link="app://cafe_action"
    ),
}
