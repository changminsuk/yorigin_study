import dataclasses
from typing import Annotated

from fastapi import Query


@dataclasses.dataclass
class CoordinatesRequest:
    longitude: Annotated[float, Query(..., example=127.00592, gt=124, lt=132)]
    latitude: Annotated[float, Query(..., example=37.49006, gt=33, lt=39)]

    def __post_init__(self) -> None:
        """
        해당 메서드는 객체가 생성된 후에 호출되는 메서드입니다.
        (__init__ 메서드가 __post_init__ 메서드를 호출합니다.)

        validation, parsing 등을 수행합니다.
            - validation: 유효성 검사 후, 유효하지 않은 경우 ValueError를 발생시킵니다.
            - parsing: 유효성 검사 후, 유효하게 변환 가능하면 변환합니다. 변환 불가능한 경우 ValueError를 발생시킵니다.
                        조회 연산에서만큼은 parsing 이 가능하면 parsing을 수행하는게 좋습니다.

        이 메서드에서는 캐싱을 용이하게 하고, 공간검색의 부하를 줄이기 위해서 round 처리를 합니다. (= parsing)
        """
        self.longitude = round(self.longitude, 5)
        self.latitude = round(self.latitude, 5)
