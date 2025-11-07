from yta_validation.parameter import ParameterValidator
from quicktions import Fraction
from typing import Union


"""
Tengo un elemento con una duración concreta, por lo que
el rango es [0, duration):
- Recortar solo por el principio => 2 segmentos
- Recortar solo por el final => 2 segmentos
- Recortar en medio => 3 segmentos
"""
Number = Union[int, float, Fraction]
"""
Custom type to represent numbers.
"""

"""
TODO: Maybe we can add the possibility of having an
`fps` value when initializing it to be able to force
the time interval values to be multiple of `1/fps`.
But this, if implemented, should be `TimeIntervalFPS`
or similar, and inheritance from this one but forcing
the values to be transformed according to that `1/fps`.
"""
class TimeInterval:
    """
    Class to represent a time interval, which is a tuple
    of time moments representing the time range 
    `[start, end)`.
    """

    @property
    def start_base(
        self
    ) -> float:
        """
        The `start` of the interval but always as 0.
        """
        return 0
    
    @property
    def end_base(
        self
    ) -> float:
        """
        The `end` of the interval but adapted to a `start=0`.
        """
        return self.end - self.start
    
    @property
    def duration(
        self
    ) -> float:
        """
        The `duration` of the time interval.
        """
        return self.end - self.start
    
    @property
    def copy(
        self
    ) -> 'TimeInterval':
        """
        A copy of this instance.
        """
        return TimeInterval(
            start = self.start,
            end = self.end
        )
    
    @property
    def as_tuple(
        self
    ) -> tuple[float, float]:
        """
        The time interval but as a `(start, end)` tuple.
        """
        return (self.start, self.end)

    def __init__(
        self,
        start: Number,
        end: Number,
    ):
        """
        Provide the interval as it actually is, with the `start`
        and `end`. These values will be adjusted to an internal
        interval starting on 0.

        The `end` value must be greater than the `start` value.
        """
        if start > end:
            raise Exception('The `start` value provided is greater than the `end` value provided.')
        
        if start == end:
            raise Exception('The `start` value provided is exactly the `end` value provided.')

        self.start: float = start
        """
        The original `start` of the time segment.
        """
        self.end: float = end
        """
        The original `end` of the time segment.
        """

    def _validate_t(
        self,
        t: Number,
        do_include_start: bool = False,
        do_include_end: bool = False
    ) -> None:
        """
        Validate that the provided `t` value is between the `start`
        and the `end` parameters provided, including them or not
        according to the boolean parameters provided.
        """
        ParameterValidator.validate_mandatory_number_between(
            name = 't',
            value = t,
            lower_limit = self.start,
            upper_limit = self.end,
            do_include_lower_limit = do_include_start,
            do_include_upper_limit = do_include_end
        )

    def _cut(
        self,
        start: Number,
        end: Number
    ) -> tuple[Union['TimeInterval', None], Union['TimeInterval', None], Union['TimeInterval', None]]:
        """
        *For internal use only*

        Cut a segment with the given `start` and `end` time moments.

        This method will return a tuple of 3 elements including the
        segments created by cutting this time interval. The tuple 
        will include all the segments at the begining and the rest
        will be None.

        Examples below:
        - A time interval of `[2, 5)` cut with `start=3` and `end=4`
        will generate `((2, 3), (3, 4), (4, 5))`.
        - A time interval of `[2, 5)` cut with `start=2` and `end=4`
        will generate `((2, 4), (4, 5), None)`.
        - A time interval of `[2, 5)` cut with `start=4` and `end=5`
        will generate `((2, 4), (4, 5), None)`.
        - A time interval of `[2, 5)` cut with `start=2` and `end=5`
        will generate `((2, 5), None, None)`.

        As you can see, the result could be the same in different
        situations, but it's up to you (and the specific method in
        which you are calling to this one) to choose the tuple you
        want to return.

        (!) This will not modify the original instance.
        """
        self._validate_t(start, do_include_start = True)
        self._validate_t(end, do_include_end = True)

        return (
            (
                self.copy,
                None,
                None
            )
            if (
                start == self.start and
                end == self.end
            ) else
            (
                TimeInterval(
                    start = self.start,
                    end = end
                ),
                TimeInterval(
                    start = end,
                    end = self.end
                ),
                None
            )
            if start == self.start else
            (
                TimeInterval(
                    start = self.start,
                    end = start
                ),
                TimeInterval(
                    start = start,
                    end = self.end
                ),
                None
            )
            if end == self.end else
            (
                TimeInterval(
                    start = self.start,
                    end = start
                ),
                TimeInterval(
                    start = start,
                    end = end
                ),
                TimeInterval(
                    start = end,
                    end = self.end
                )
            )
        )

    def cut_from_start_to(
        self,
        t: Number,
        do_get_cut: bool = False
    ) -> Union['TimeInterval', None]:
        """
        Cut the interval from the start to the `t` value
        provided. The return will be the segment cut if 
        `do_get_cut` is False, or the remaining part if
        True.

        (!) This will not modify the original instance.
        """
        intervals = self._cut(
            start = self.start,
            end = t
        )

        return (
            intervals[0]
            if (
                len(intervals) == 1 or
                do_get_cut
            ) else
            intervals[1]
        )
    
    def cut_to_end_from(
        self,
        t: Number,
        do_get_cut: bool = False
    ) -> Union['TimeInterval', None]:
        """
        Cut the interval from the start to the `t` value
        provided. The return will be the segment cut if 
        `do_get_cut` is False, or the remaining part if
        True.

        (!) This will not modify the original instance.
        """
        intervals = self._cut(
            start = t,
            end = self.end
        )

        return (
            intervals[0]
            if (
                len(intervals) == 1 or
                not do_get_cut
            ) else
            intervals[1]
        )
    
    def cut_from_to(
        self,
        from_t: Number,
        to_t: Number,
        # do_get_cut: bool = False
    ) -> Union['TimeInterval', None]:
        """
        Cut the interval from the `from_t` value provided
        to the `to_t` value given. The return will be the
        segment cut.

        (!) This will not modify the original instance.

        TODO: By now we are only getting the cut
        """
        intervals = self._cut(
            start = from_t,
            end = to_t
        )
        
        return (
            intervals[0]
            if (
                len(intervals) == 1 or
                (
                    len(intervals) == 2 and
                    from_t == self.start
                )
            ) else
            intervals[1]
        )
    
    def is_t_included(
        self,
        t: float,
        do_include_end: bool = False
    ) -> bool:
        """
        Check if the `t` time moment provided is included in
        this time interval, including the `end` only if the
        `do_include_end` parameter is set as `True`.
        """
        return TimeIntervalUtils.a_includes_t(
            t = t,
            time_interval_a = self,
            do_include_end = do_include_end
        )
    
    def is_adjacent_to(
        self,
        time_interval: 'TimeInterval'
    ) -> bool:
        """
        Check if the `time_interval` provided is adjacent
        to this time interval, which means that the `end`
        of one interval is also the `start` of the other
        one.

        (!) Giving the time intervals inverted will
        provide the same result.

        Example below:
        - `a=[2, 5)` and `b=[5, 7)` => `True`
        - `a=[5, 7)` and `b=[2, 5)` => `True`
        - `a=[2, 5)` and `b=[3, 4)` => `False`
        - `a=[2, 5)` and `b=[6, 8)` => `False`
        """
        return TimeIntervalUtils.a_is_adjacent_to_b(
            time_interval_a = self,
            time_interval_b = time_interval
        )
    
    def do_contains_a(
        self,
        time_interval: 'TimeInterval'
    ) -> bool:
        """
        Check if this time interval includes the `time_interval`
        provided or not, which means that the `time_interval`
        provided is fully contained (included) in this one.
        """
        return TimeIntervalUtils.a_contains_b(
            time_interval_a = self,
            time_interval_b = time_interval
        )
    
    def is_contained_in(
        self,
        time_interval: 'TimeInterval'
    ) -> bool:
        """
        Check if this time interval is fully contained in
        the `time_interval` provided, which is a synonim
        of being fully overlapped by that `time_interval`.
        """
        return TimeIntervalUtils.a_is_contained_in_b(
            time_interval_a = self,
            time_interval_b = time_interval
        )
    
    def do_intersects_with(
        self,
        time_interval: 'TimeInterval'
    ) -> bool:
        """
        Check if this time interval intersects with the one
        provided as `time_interval`, which means that they
        have at least a part in common.
        """
        return TimeIntervalUtils.a_intersects_with_b(
            time_interval_a = self,
            time_interval_b = time_interval
        )
    
    def get_intersection_with_a(
        self,
        time_interval: 'TimeInterval'
    ) -> Union['TimeInterval', None]:
        """
        Get the time interval that intersects this one and the
        one provided as `time_interval`. The result can be `None`
        if there is no intersection in between both.
        """
        return TimeIntervalUtils.get_intersection_of_a_and_b(
            time_interval_a = self,
            time_interval_b = time_interval
        )
    
    
class TimeIntervalUtils:
    """
    Static class to wrap the utils related to time intervals.
    """

    @staticmethod
    def a_includes_t(
        t: float,
        time_interval_a: 'TimeInterval',
        do_include_end: bool = False
    ) -> bool:
        """
        Check if the `t` time moment provided is included in
        the `time_interval_a` given. The `time_interval_a.end`
        is excluded unless the `do_include_end` parameter is
        set as `True`.

        A time interval is `[start, end)`, thats why the end is
        excluded by default.
        """
        return (
            time_interval_a.start <= t <= time_interval_a.end
            if do_include_end else
            time_interval_a.start <= t < time_interval_a.end
        )
    
    @staticmethod
    def a_is_adjacent_to_b(
        time_interval_a: 'TimeInterval',
        time_interval_b: 'TimeInterval',
    ) -> bool:
        """
        Check if the `time_interval_a` provided and the
        also given `time_interval_b` are adjacent, which
        means that the `end` of one interval is also the
        `start` of the other one.

        (!) Giving the time intervals inverted will
        provide the same result.

        Examples below:
        - `a=[2, 5)` and `b=[5, 7)` => `True`
        - `a=[5, 7)` and `b=[2, 5)` => `True`
        - `a=[2, 5)` and `b=[3, 4)` => `False`
        - `a=[2, 5)` and `b=[6, 8)` => `False`
        """
        return (
            TimeIntervalUtils.a_is_inmediately_before_b(time_interval_a, time_interval_b) or
            TimeIntervalUtils.a_is_inmediately_after_b(time_interval_a, time_interval_b)
        )
    
    @staticmethod
    def a_is_inmediately_before_b(
        time_interval_a: 'TimeInterval',
        time_interval_b: 'TimeInterval',
    ) -> bool:
        """
        Check if the `time_interval_a` provided is inmediately
        before the also given `time_interval_b`, which means
        that the `end` of the first one is also the `start` of
        the second one.

        Examples below:
        - `a=[2, 5)` and `b=[5, 7)` => `True`
        - `a=[5, 7)` and `b=[2, 5)` => `False`
        - `a=[2, 5)` and `b=[3, 4)` => `False`
        - `a=[2, 5)` and `b=[6, 8)` => `False`
        """
        return time_interval_a.end == time_interval_b.start
    
    @staticmethod
    def a_is_inmediately_after_b(
        time_interval_a: 'TimeInterval',
        time_interval_b: 'TimeInterval',
    ) -> bool:
        """
        Check if the `time_interval_a` provided is inmediately
        after the also given `time_interval_b`, which means
        that the `start` of the first one is also the `end` of
        the second one.

        Examples below:
        - `a=[2, 5)` and `b=[5, 7)` => `False`
        - `a=[5, 7)` and `b=[2, 5)` => `True`
        - `a=[2, 5)` and `b=[3, 4)` => `False`
        - `a=[2, 5)` and `b=[6, 8)` => `False`
        """
        return time_interval_a.start == time_interval_b.end
    
    @staticmethod
    def a_contains_b(
        time_interval_a: 'TimeInterval',
        time_interval_b: 'TimeInterval'
    ) -> bool:
        """
        Check if the `time_interval_a` time interval provided
        includes the `time_interval_b` or not, which means that
        the `time_interval_b` is fully contained in the first
        one.

        Examples below:
        - `a=[2, 5)` and `b=[3, 4)` => `True`
        - `a=[2, 5)` and `b=[2, 4)` => `True`
        - `a=[2, 5)` and `b=[3, 6)` => `False`
        - `a=[2, 5)` and `b=[6, 8)` => `False`
        """
        return (
            time_interval_a.start <= time_interval_b.start and
            time_interval_a.end >= time_interval_b.end
        )
    
    @staticmethod
    def a_is_contained_in_b(
        time_interval_a: 'TimeInterval',
        time_interval_b: 'TimeInterval',
    ) -> bool:
        """
        Check if the `time_interval_a` provided is fully
        contained into the also provided `time_interval_b`.

        Examples below:
        - `a=[2, 5)` and `b=[1, 6)` => `True`
        - `a=[2, 5)` and `b=[0, 9)` => `True`
        - `a=[2, 5)` and `b=[2, 4)` => `False`
        - `a=[2, 5)` and `b=[4, 8)` => `False`
        - `a=[2, 5)` and `b=[7, 8)` => `False`
        """
        return TimeIntervalUtils.a_contains_b(
            time_interval_a = time_interval_b,
            time_interval_b = time_interval_a
        )
    
    @staticmethod
    def a_intersects_with_b(
        time_interval_a: 'TimeInterval',
        time_interval_b: 'TimeInterval',
    ) -> bool:
        """
        Check if the `time_interval_a` and the `time_interval_b`
        provided has at least a part in common.

        Examples below:
        - `a=[2, 5)` and `b=[4, 6)` => `True`
        - `a=[2, 5)` and `b=[1, 3)` => `True`
        - `a=[2, 5)` and `b=[5, 6)` => `False`
        - `a=[2, 5)` and `b=[7, 8)` => `False`
        - `a=[2, 5)` and `b=[1, 2)` => `False`
        """
        return (
            time_interval_b.start < time_interval_a.end and
            time_interval_a.start < time_interval_b.end
        )
    
    @staticmethod
    def get_intersection_of_a_and_b(
        time_interval_a: 'TimeInterval',
        time_interval_b: 'TimeInterval'
    ) -> Union['TimeInterval', None]:
        """
        Get the time interval that intersects the two time
        intervals provided, that can be `None` if there is no
        intersection in between both.
        """
        return (
            None
            if not TimeIntervalUtils.a_intersects_with_b(
                time_interval_a = time_interval_a,
                time_interval_b = time_interval_b
            ) else
            TimeInterval(
                start = max(time_interval_a.start, time_interval_b.start),
                end = min(time_interval_a.end, time_interval_b.end)
            )
        )
