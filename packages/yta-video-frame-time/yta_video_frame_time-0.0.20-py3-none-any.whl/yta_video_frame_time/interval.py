"""
TODO: This module is general so we should send it
to another library related to time intervals and
not specifically video frame times... Move it.
"""
from yta_video_frame_time.decorators import parameter_to_time_interval
from yta_video_frame_time.t_fraction import THandler
from yta_validation.parameter import ParameterValidator
from quicktions import Fraction
from typing import Union


Number = Union[int, float, Fraction]
"""
Custom type to represent numbers.
"""
TimeIntervalType = Union['TimeInterval', tuple[float, float]]
"""
The type we accept as time interval, that could be a
tuple we transform into a time interval.
"""
TIME_INTERVAL_SYSTEM_LIMITS = (0, 9999)
"""
The limits for the `start` and `end` fields of any
time interval that the system will apply if no limits
are requested by the user.

The limits are `0` and `9999`.
"""

class TimeInterval:
    """
    A time interval that has a memory of the original values
    but can be modified and enshorted during its life time.

    Class to represent a time interval, which is a tuple
    of time moments representing the time range 
    `[start, end)`.

    TODO: This will replace the old two versions by making
    the 'fps' parameter optional.
    """

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
        time_interval = TimeInterval(
            start = self.start,
            end = self.end,
            start_limit = self.start_limit,
            end_limit = self.end_limit,
            fps = self.fps
        )

        return time_interval
    
    @property
    def as_tuple(
        self
    ) -> tuple[float, float]:
        """
        The time interval but as a `(start, end)` tuple.
        """
        return (self.start, self.end)
    
    @property
    def _cutter(
        self
    ) -> 'TimeIntervalCutter':
        """
        Shortcut to the static class `TimeIntervalCutter` that
        is capable of cutting time intervals.
        """
        return TimeIntervalCutter
    
    @property
    def _extender(
        self
    ) -> 'TimeIntervalExtender':
        """
        Shortcut to the static class `TimeIntervalExtender` that
        is capable of extending time intervals.
        """
        return TimeIntervalExtender
    
    @property
    def _utils(
        self
    ) -> 'TimeIntervalUtils':
        """
        Shortcut to the static class `TimeIntervalUtils` that
        is capable of extending time intervals.
        """
        return TimeIntervalUtils

    def __init__(
        self,
        start: Number,
        end: Number,
        start_limit: Union[Number, None] = None,
        end_limit: Union[Number, None] = None,
        # TODO: Implement a 'duration_limit'
        fps: Union[Number, None] = None
    ):
        """
        The `end` value must be greater than the `start` value.

        (!) If `fps` is provided, the `start`, `end`, `start_limit`
        and `end_limit` values will be truncated according to the
        `fps` provided.

        (!) If no `start_limit` and/or no `end_limit` values are
        provided, the ones from the system will be applied.
        """
        ParameterValidator.validate_positive_number('fps', fps, do_include_zero = False)
        ParameterValidator.validate_mandatory_positive_number('start', start, do_include_zero = True)
        ParameterValidator.validate_mandatory_positive_number('end', end, do_include_zero = False)
        ParameterValidator.validate_positive_number('start_limit', start_limit, do_include_zero = True)
        ParameterValidator.validate_positive_number('end_limit', end_limit, do_include_zero = False)

        self.fps: Union[Number, None] = fps
        """
        The `fps` for this time interval calculations, if set.
        """
        self._t_handler: Union[THandler, None] = (
            THandler(self.fps)
            if self.fps is not None else
            None
        )
        """
        *For internal use only*

        Shortcut to the `THandler` instance built with the `fps`
        value provided when instantiating this instance, that
        can be `None` if no `fps` are provided.
        """

        start_limit = self._truncate(
            TIME_INTERVAL_SYSTEM_LIMITS[0]
            if start_limit is None else
            start_limit
        )

        end_limit = self._truncate(
            TIME_INTERVAL_SYSTEM_LIMITS[1]
            if end_limit is None else
            end_limit
        )

        if start_limit < TIME_INTERVAL_SYSTEM_LIMITS[0]:
            raise Exception(f'The `start_limit` provided ({str(float(start_limit))}) is lower than the system limit ({str(float(TIME_INTERVAL_SYSTEM_LIMITS[0]))})')
        
        if end_limit > TIME_INTERVAL_SYSTEM_LIMITS[1]:
            raise Exception(f'The `end_limit` provided ({str(float(end_limit))}) is greater than the system limit ({str(float(TIME_INTERVAL_SYSTEM_LIMITS[1]))})')
        
        self.start_limit: Fraction = start_limit
        """
        The limit for the `start` of this time interval, which
        will be used to raise exceptions if any of the `start`
        values goes beyond this limit.

        See the `TIME_INTERVAL_SYSTEM_LIMITS[0]` variable to
        know the limit defined by the system that will be
        applied if the user doesn't provided his own limit.
        """
        self.end_limit: Fraction = end_limit
        """
        The limit for the `end` of this time interval, which
        will be used to raise exceptions if any of the `end`
        values goes beyond this limit.

        See the `TIME_INTERVAL_SYSTEM_LIMITS[1]` variable to
        know the limit defined by the system that will be
        applied if the user doesn't provided his own limit.
        """

        self.start: Fraction = self._truncate(start)
        """
        The current `start` value of this time interval.
        """
        self.end: Fraction = self._truncate(end)
        """
        The current `end` value of this time interval.
        """

        self._validate_start(self.start)
        self._validate_end(self.end)

    def _validate_start(
        self,
        start: Union[Number, None]
    ) -> None:
        """
        *For internal use only*

        Validate that the `start` value provided is accepted by the
        time interval and the system based on the limits and the
        value of the `end` parameter also.

        This method will raise an exception if the provided value is
        not valid.
        """
        if start >= self.end:
            raise Exception(f'The `start` value provided ({str(float(start))}) is greater or equal to the current`end` value ({str(float(self.end))}).')
        
        if start < self.start_limit:
            raise Exception(f'The `start` value provided ({str(float(start))}) is lower than the `start_limit` ({str(float(self.start_limit))}).')
        
    def _validate_end(
        self,
        end: Union[Number, None]
    ) -> None:
        """
        *For internal use only*

        Validate that the `end` value provided is accepted by the
        time interval and the system based on the limits and the
        value of the `start` parameter also.

        This method will raise an exception if the provided value is
        not valid.
        """
        if end <= self.start:
            raise Exception(f'The `end` value provided ({str(float(end))}) is lower or equal to the current`start` value ({str(float(self.start))}).')
        
        if end > self.end_limit:
            raise Exception(f'The `end` value provided ({str(float(end))}) is greater than the `end_limit` ({str(float(self.end_limit))}).')

    """
    Apparently, the professional video editors use always
    the `truncate` method to obtain the `start` of the
    frame time interval always. So, why should I change it?
    """
    def _truncate(
        self,
        t: Number
    ) -> float:
        """
        *For internal use only*

        Get the truncated value of the `t` time moment provided,
        which will be always the `start` of the time interval
        delimited by the `t` and the `fps` of this instance.

        (!) The value will be truncated only if the `fps`
        attribute is set.

        Some examples below (with `fps=5`):
        - `t=0.2` => `0.2` <=> `interval=[0.2, 0.4)`
        - `t=0.37` => `0.2` <=> `interval=[0.2, 0.4)`
        - `t=0.4` => `0.4` <=> `interval=[0.4, 0.6)`
        - `t=0.87` => `0.8` <=> `interval=[0.8, 1.0)`
        """
        return (
            self._t_handler.t.truncated(t)
            if self.fps is not None else
            t
        )
    
    def _round(
        self,
        t: Number
    ) -> float:
        """
        *For internal use only*

        Get the rounded value of the `t` time moment provided,
        which will be the `start` or the `end` (depending on which
        one is closer to the `t` value) of the time interval
        delimited by the `t` and the `fps` of this instance.

        (!) The value will be rounded only if the `fps`
        attribute is set.

        Some examples below (with `fps=5`):
        - `t=0.2` => `0.2` <=> `interval=[0.2, 0.4)`
        - `t=0.29` => `0.2` <=> `interval=[0.2, 0.4)`
        - `t=0.31` => `0.4` <=> `interval=[0.2, 0.4)`
        - `t=0.37` => `0.4` <=> `interval=[0.2, 0.4)`
        - `t=0.4` => `0.4` <=> `interval=[0.4, 0.6)`
        - `t=0.87` => `0.8` <=> `interval=[0.8, 1.0)`
        """
        return (
            self._t_handler.t.rounded(t)
            if self.fps is not None else
            t
        )
    
    def _round_up(
        self,
        t: Number
    ) -> float:
        """
        *For internal use only*
        
        Get the rounded up value of the `t` time moment provided,
        which will be the `end` of the time interval (unless it
        is exactly the `start` value of a time interval) delimited
        by the `t` and the `fps` of this instance.

        (!) The value will be rounded up only if the `fps`
        attribute is set.

        Some examples below (with `fps=5`):
        - `t=0.2` => `0.2` <=> `interval=[0.2, 0.4)`
        - `t=0.29` => `0.4` <=> `interval=[0.2, 0.4)`
        - `t=0.31` => `0.4` <=> `interval=[0.2, 0.4)`
        - `t=0.37` => `0.2` <=> `interval=[0.2, 0.4)`
        - `t=0.4` => `0.4` <=> `interval=[0.4, 0.6)`
        - `t=0.87` => `0.8` <=> `interval=[0.8, 1.0)`
        """
        return (
            self._t_handler.t.rounded_up(t)
            if self.fps is not None else
            t
        )
    
    def is_t_included(
        self,
        t: Number,
        do_include_end: bool = False
    ) -> bool:
        """
        Check if the `t` time moment provided is included in
        in this time interval instance current limits or not.
        This means that the `t` provided is between the
        current `start` and `end` time moment values.

        The `end` can be included for some special cases by
        providing the `do_include_end` boolean parameter as
        `True`.
        """
        return self._utils.a_includes_t(
            t = t,
            time_interval_a = self,
            do_include_end = do_include_end
        )
    
    def is_t_included_in_limits(
        self,
        t: Number
    ) -> bool:
        """
        Check if the `t` time moment provided is included in
        in this time interval instance if the original limits
        were the current `start` and `end` or not.

        This will return `True` if the `t` provided is between
        the `start_limit` and `end_limit` values.

        The `end_limit` is not included.
        """
        return self.start_limit <= t < self.end_limit
    
    @parameter_to_time_interval('time_interval')
    def is_adjacent_to(
        self,
        time_interval: TimeIntervalType
    ) -> bool:
        """
        Check if this time interval and the one provided as
        `time_interval` are adjacent, which means that the
        `end` of one interval is also the `start` of the
        other one.

        (!) Giving the time intervals inverted will
        provide the same result.

        Examples below:
        - `a=[2, 5)` and `b=[5, 7)` => `True`
        - `a=[5, 7)` and `b=[2, 5)` => `True`
        - `a=[2, 5)` and `b=[3, 4)` => `False`
        - `a=[2, 5)` and `b=[6, 8)` => `False`
        """
        return self._utils.a_is_adjacent_to_b(
            time_interval_a = self,
            time_interval_b = time_interval
        )
    
    @parameter_to_time_interval('time_interval')
    def is_contained_in(
        self,
        time_interval: TimeIntervalType
    ) -> bool:
        """
        Check if this time interval is fully contained
        into the one provided as `time_interval`.

        Examples below:
        - `a=[2, 5)` and `b=[1, 6)` => `True`
        - `a=[2, 5)` and `b=[0, 9)` => `True`
        - `a=[2, 5)` and `b=[2, 4)` => `False`
        - `a=[2, 5)` and `b=[4, 8)` => `False`
        - `a=[2, 5)` and `b=[7, 8)` => `False`
        """
        return self._utils.a_is_contained_in_b(
            time_interval_a = self,
            time_interval_b = time_interval
        )
    
    @parameter_to_time_interval('time_interval')
    def do_intersects_with(
        self,
        time_interval: TimeIntervalType
    ) -> bool:
        """
        Check if this time interval and the one provided
        as `time_interval` have at least a part in common.

        Examples below:
        - `a=[2, 5)` and `b=[4, 6)` => `True`
        - `a=[2, 5)` and `b=[1, 3)` => `True`
        - `a=[2, 5)` and `b=[5, 6)` => `False`
        - `a=[2, 5)` and `b=[7, 8)` => `False`
        - `a=[2, 5)` and `b=[1, 2)` => `False`
        """
        return self._utils.a_intersects_with_b(
            time_interval_a = self,
            time_interval_b = time_interval
        )
    
    @parameter_to_time_interval('time_interval')
    def get_intersection_with(
        self,
        time_interval: TimeIntervalType
    ) -> Union['TimeInterval', None]:
        """
        Get the time interval that intersects this time
        interval and the one provided as `time_interval`,
        that can be `None` if there is no intersection in
        between both.
        """
        return self._utils.get_intersection_of_a_and_b(
            time_interval_a = self,
            time_interval_b = time_interval
        )

    # Modifying 'start' and 'end' below
    def shift(
        self,
        delta: Number
    ) -> 'TimeInterval':
        """
        (!) This method will modify this instance.
        
        Move the `start` and the `end` by applying the `delta`
        amount (that will be forced to be a multiple of `1/fps`)
        but modifying not the duration.

        This can only be done if the new `start` and `end` values
        are in between  the limits.
        """
        delta = self._truncate(delta)

        new_start = self.start + delta
        new_end = self.end + delta
        
        if delta > 0:
            self._validate_end(new_end)
            self._validate_start(new_start)
        else:
            self._validate_start(new_start)
            self._validate_end(new_end)
        
        self.start = new_start
        self.end = new_end

        return self

    def get_cuts(
        self,
        start: Number,
        end: Number
    ) -> tuple[Union['TimeInterval', None], Union['TimeInterval', None], Union['TimeInterval', None]]:
        """
        Cut a segment from the given `start` to the also provided
        `end` time moments of this time interval instance and get
        all the cuts.

        This method will return a tuple of 3 elements including the
        segments created by cutting this time interval in the order
        they were generated, but also having the 4th element always
        as the index of the one specifically requested by the user.
        The tuple will include all the segments at the begining and
        the rest will be None (unless the 4th one, which is the
        index).

        Examples below:
        - A time interval of `[2, 5)` cut with `start=3` and `end=4`
        will generate `((2, 3), (3, 4), (4, 5), 1)`.
        - A time interval of `[2, 5)` cut with `start=2` and `end=4`
        will generate `((2, 4), (4, 5), None, 0)`.
        - A time interval of `[2, 5)` cut with `start=4` and `end=5`
        will generate `((2, 4), (4, 5), None, 1)`.
        - A time interval of `[2, 5)` cut with `start=2` and `end=5`
        will generate `((2, 5), None, None, 0)`.

        As you can see, the result could be the same in different
        situations, but it's up to you (and the specific method in
        which you are calling to this one) to choose the tuple you
        want to return.
        """
        return self._cutter.from_to(
            time_interval = self,
            start = self._truncate(start),
            end = self._truncate(end)
        )
    
    def get_cut(
        self,
        start: Number,
        end: Number
    ) -> 'TimeInterval':
        """
        Get this time interval instance but cutted from the `start`
        to the `end` time moments provided.

        (!) This method doesn't modify the original instance but
        returns a new one.
        """
        tuples = self.get_cuts(
            start = start,
            end = end
        )

        return tuples[tuples[3]]
    
    def cut(
        self,
        start: Number,
        end: Number
    ) -> 'TimeInterval':
        """
        (!) This method will modify this instance.

        Transform this time interval into a new one delimited by
        the `start` and `end` time moments provided.

        This method returns this same instance but modified.
        """
        cut = self.get_cut(
            start = start,
            end = end
        )

        self.start = cut.start
        self.end = cut.end

        return self
    
    # TODO: Rename, please
    def get_trim_starts(
        self,
        t_variation: Number
    ) -> tuple['TimeInterval', 'TimeInterval']:
        """
        Get a tuple containing the 2 new `TimeInterval` instances
        generated by trimming this one's start the amount of seconds
        provided as the `t_variation` parameter. The first tuple is
        the remaining, and the second one is the new time interval
        requested by the user.

        (!) The `t_variation` value provided will be transformed into
        a multiple of `1/fps` of this instance, and truncated to fit
        the `start` of the time interval the new segments will belong
        to, if the `fps` is set.

        This method will raise an exception if the new `start` value
        becomes a value over the time interval `end` value or the
        `limit`, that must be greater than the `start` and lower
        than the time interval `end` value.

        The `t_variation` must be a positive value, the amount of
        seconds to be trimmed.
        """
        return self._cutter.trim_start(
            time_interval = self,
            t_variation = self._truncate(t_variation)
        )
    
    # TODO: Rename, please
    def get_trim_start(
        self,
        t_variation: Number
    ) -> 'TimeInterval':
        """
        Get this time interval instance but trimmed from the `start`
        the `t_variation` amount of seconds provided.

        (!) The `t_variation` value provided will be transformed into
        a multiple of `1/fps` of this instance, and truncated to fit
        the `start` of the time interval the new segments will belong
        to, if the `fps` is set.

        (!) This method doesn't modify the original instance but
        returns a new one.
        """
        return self.get_trim_starts(
            t_variation = t_variation
        )[1]
    
    def _trim_start(
        self,
        t_variation: Number
    ) -> 'TimeInterval':
        """
        (!) This method will modify this instance.

        Transform this time interval into a new one in which
        the `start` has been trimmed the `t_variation` provided
        if the result respected the also given `limit`.

        This method returns this same instance but modified.
        """
        cut = self.get_trim_start(
            t_variation = t_variation
        )

        self.start = cut.start
        self.end = cut.end

        return self
    
    def get_trim_ends(
        self,
        t_variation: Number
    ) -> tuple['TimeInterval', 'TimeInterval']:
        """
        Get a tuple containing the 2 new `TimeInterval` instances
        generated by trimming this one's end the amount of seconds
        provided as the `t_variation` parameter. The first tuple is
        the one requested by the user, and the second one is the
        remaining.

        (!) The `t_variation` value provided will be transformed into
        a multiple of `1/fps` of this instance, and truncated to fit
        the `start` of the time interval the new segments will belong
        to, if the `fps` is set.

        The `t_variation` must be a positive value, the amount of
        seconds to be trimmed.
        """
        return self._cutter.trim_end(
            time_interval = self,
            t_variation = self._truncate(t_variation)
        )
    
    # TODO: Rename, please
    def get_trim_end(
        self,
        t_variation: Number
    ) -> 'TimeInterval':
        """
        Get this time interval instance but trimmed from the `end`
        the `t_variation` amount of seconds provided.

        (!) The `t_variation` value provided will be transformed into
        a multiple of `1/fps` of this instance, and truncated to fit
        the `end` of the time interval the new segments will belong
        to, if the `fps` is set.

        (!) This method doesn't modify the original instance but
        returns a new one.
        """
        return self.get_trim_ends(
            t_variation = t_variation
        )[0]
    
    def _trim_end(
        self,
        t_variation: Number
    ) -> 'TimeInterval':
        """
        (!) This method will modify this instance.

        Transform this time interval into a new one in which
        the `end` has been trimmed the `t_variation` provided
        if the result respected the also given `limit`.

        This method returns this same instance but modified.
        """
        cut = self.get_trim_end(
            t_variation = t_variation
        )

        self.start = cut.start
        self.end = cut.end

        return self
    
    def get_splits(
        self,
        t: Number
    ) -> tuple['TimeInterval', 'TimeInterval']:
        """
        Split the time interval at the provided `t` time moment
        and get the 2 new time intervals as a result (as a tuple).

        (!) The `t` value provided will be transformed into a
        multiple of `1/fps` of this instance, and truncated to fit
        the `start` of the time interval the new segments will belong
        to if the `fps` value is set.

        This method will raise an exception if the `t` value 
        provided is a limit value (or above).

        Examples below:
        - A time interval of `[2, 5)` cut with `t=3` will generate
        `((2, 3), (3, 5))`.
        - A time interval of `[2, 5)` cut with `t=4` will generate
        `((2, 4), (4, 5))`.
        - A time interval of `[2, 5)` cut with `t>=5` will raise
        exception.
        - A time interval of `[2, 5)` cut with `t<=2` will raise
        exception.
        """
        return self._cutter.split(
            time_interval = self,
            t = self._truncate(t)
        )
    
    def split(
        self,
        t: Number
    ) -> tuple['TimeInterval', 'TimeInterval']:
        """
        Split the time interval at the provided `t` time moment
        and get the 2 new time intervals as a result (as a tuple),
        that will be copies of this instance (with their original
        `start` and `end` values) but the new ones according to 
        the split result.

        (!) The `t` value provided will be transformed into a
        multiple of `1/fps` of this instance, and truncated to fit
        the `start` of the time interval the new segments will belong
        to if the `fps` value is set.

        This method will raise an exception if the `t` value 
        provided is a limit value (or above).
        """
        splits = self.get_splits(t)

        split_left = self.copy
        split_left.start = splits[0].start
        split_left.end = splits[0].end

        split_right = self.copy
        split_right.start = splits[1].start
        split_right.end = splits[1].end

        return (
            split_left, split_right
        )
    
    def _extend_end(
        self,
        t_variation: Number
    ) -> 'TimeInterval':
        """
        (!) This method will modify this instance.

        Transform this time interval into a new one in which
        the `end` has been extended the `t_variation` provided
        if the result respected the also given `limit`.

        This method returns this same instance but modified.
        """
        ParameterValidator.validate_mandatory_positive_number('t_variation', t_variation, do_include_zero = False)

        extended = self._extender.extend_end(
            time_interval = self,
            t_variation = (
                self._truncate(t_variation)
                if self.fps is not None else
                t_variation
            )
        )

        # TODO: Is this above a bit useless (?)
        self.end = extended.end

        return self
    
    def _extend_start(
        self,
        t_variation: Number
    ) -> 'TimeInterval':
        """
        (!) This method will modify this instance.

        Transform this time interval into a new one in which
        the `start` has been extended the `t_variation` provided
        if the result respected the also given `limit`.

        This method returns this same instance but modified.
        """
        ParameterValidator.validate_mandatory_positive_number('t_variation', t_variation, do_include_zero = False)

        extended = self._extender.extend_start(
            time_interval = self,
            t_variation = (
                self._truncate(t_variation)
                if self.fps is not None else
                t_variation
            )
        )

        # TODO: Is this above a bit useless (?)
        self.start = extended.start

        return self
    
    def modify_start(
        self,
        t_variation: Number
    ) -> 'TimeInterval':
        """
        (!) This method will modify this instance.

        Giving a negative `t_variation` value will make the
        time interval longer, extending the `start` value.

        Transform this time interval into a new one in which
        the `start` has been extended or trimmed the
        `t_variation` value provided if the result respects 
        the also given `limit`.

        The new `start` can never be lower than the original
        (min) `start` value of this time interval instance.

        This method returns this same instance but modified.
        """
        ParameterValidator.validate_mandatory_number(t_variation, t_variation, do_include_zero = False)

        return (
            self._trim_start(
                t_variation = abs(t_variation)
            )
            if t_variation > 0 else
            self._extend_start(
                t_variation = abs(t_variation)
            )
        )
    
    def modify_start_to(
        self,
        start: Number
    ) -> 'TimeInterval':
        """
        (!) This method will modify this instance.

        Transform this time interval into a new one in which
        the `start` has been extended or trimmed until
        reaching the new `start` parameter value provided (if
        valid).

        The new `start` can never be lower than the limit
        (min) `start_limit` value of this time interval
        instance.

        This method returns this same instance but modified.
        """
        ParameterValidator.validate_mandatory_number(start, start, do_include_zero = True)

        if start != self.start:
            self._validate_start(start)
            self.start = start

        return self
    
    def modify_end(
        self,
        t_variation: Number
    ) -> 'TimeInterval':
        """
        (!) This method will modify this instance.

        Giving a positive `t_variation` value will make the
        time interval longer, extending the `end` value.

        Transform this time interval into a new one in which
        the `end` has been extended or trimmed the
        `t_variation` value provided if the result respects 
        the also given `limit`.

        The new `end` can never be greater than the original
        (min) `end` value of this time interval instance.

        This method returns this same instance but modified.
        """
        ParameterValidator.validate_mandatory_number(t_variation, t_variation, do_include_zero = False)

        return (
            self._trim_end(
                t_variation = abs(t_variation)
            )
            if t_variation < 0 else
            self._extend_end(
                t_variation = abs(t_variation)
            )
        )
    
    def modify_end_to(
        self,
        t: Number
    ) -> 'TimeInterval':
        """
        (!) This method will modify this instance.

        Transform this time interval into a new one in which
        the `end` has been extended or trimmed until
        reaching the new `t` parameter value provided (if
        valid).

        The new `end` can never be greater than the original
        (min) `end` value of this time interval instance.

        This method returns this same instance but modified.
        """
        ParameterValidator.validate_mandatory_number(t, t, do_include_zero = True)

        if end != self.end:
            self._validate_end(end)
            self.end = end

        return self
        
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
        provided have at least a part in common.

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

        The `fps` of the intersection will be `None`.
        """
        return (
            None
            if not TimeIntervalUtils.a_intersects_with_b(
                time_interval_a = time_interval_a,
                time_interval_b = time_interval_b
            ) else
            TimeInterval(
                start = max(time_interval_a.start, time_interval_b.start),
                end = min(time_interval_a.end, time_interval_b.end),
                start_limit = min(time_interval_a.start_limit, time_interval_b.start_limit),
                end_limit = max(time_interval_a.end_limit, time_interval_b.end_limit),
                fps = None
            )
        )

class TimeIntervalCutter:
    """
    Class to wrap the functionality related to cutting
    time intervals.
    """

    @staticmethod
    @parameter_to_time_interval('time_interval')
    def trim_end_to(
        time_interval: TimeIntervalType,
        t: Number
    ) -> tuple['TimeInterval', 'TimeInterval']:
        """
        Get a tuple containing the 2 new `TimeInterval` instances
        generated by trimming the `time_interval` end to the `t`
        time moment provided. The first tuple is the requested by
        the user, and the second one is the remaining.

        The `t` time moment provided must be a value between the
        `start` and `end` of the `time_interval` provided.
        """
        _validate_time_interval_current_limits(time_interval, t)
        
        return (
            TimeInterval(
                start = time_interval.start,
                end = t,
                start_limit = time_interval.start_limit,
                end_limit = time_interval.end_limit,
                fps = time_interval.fps
            ),
            TimeInterval(
                start = t,
                end = time_interval.end,
                start_limit = time_interval.start_limit,
                end_limit = time_interval.end_limit,
                fps = time_interval.fps
            )
        )
    
    @staticmethod
    @parameter_to_time_interval('time_interval')
    def trim_end(
        time_interval: TimeIntervalType,
        t_variation: Number
    ) -> tuple['TimeInterval', 'TimeInterval']:
        """
        Get a tuple containing the 2 new `TimeInterval` instances
        generated by trimming the `time_interval` end the amount
        of seconds provided as the `t_variation` parameter. The
        first tuple is the requested by the user, and the second one
        is the remaining.

        The `t_variation` must be a positive value, the amount of
        seconds to be trimmed.
        """
        ParameterValidator.validate_mandatory_positive_number('t_variation', t_variation, do_include_zero = False)

        return TimeIntervalCutter.trim_end_to(
            time_interval = time_interval,
            t = time_interval.end - t_variation
        )
    
    @staticmethod
    @parameter_to_time_interval('time_interval')
    def trim_start_to(
        time_interval: TimeIntervalType,
        t: Number
    ) -> tuple['TimeInterval', 'TimeInterval']:
        """
        Get a tuple containing the 2 new `TimeInterval` instances
        generated by trimming the `time_interval` start to the `t`
        time moment provided. The first tuple is the remaining, and
        the second one is the requested by the user.

        The `t` time moment provided must be a value between the
        `start` and `end` of the `time_interval` provided.
        """
        _validate_time_interval_current_limits(time_interval, t)
        
        return (
            TimeInterval(
                start = time_interval.start,
                end = t,
                start_limit = time_interval.start_limit,
                end_limit = time_interval.end_limit,
                fps = time_interval.fps
            ),
            TimeInterval(
                start = t,
                end = time_interval.end,
                start_limit = time_interval.start_limit,
                end_limit = time_interval.end_limit,
                fps = time_interval.fps
            )
        )
    
    @staticmethod
    @parameter_to_time_interval('time_interval')
    def trim_start(
        time_interval: TimeIntervalType,
        t_variation: Number
    ) -> tuple['TimeInterval', 'TimeInterval']:
        """
        Get a tuple containing the 2 new `TimeInterval` instances
        generated by trimming the `time_interval` start the amount
        of seconds provided as the `t_variation` parameter. The
        first tuple is the remaining, and the second one is the
        new time interval requested by the user.

        The `t_variation` must be a positive value, the amount of
        seconds to be trimmed.
        """
        ParameterValidator.validate_mandatory_positive_number('t_variation', t_variation, do_include_zero = False)

        return TimeIntervalCutter.trim_start_to(
            time_interval = time_interval,
            t = time_interval.start + t_variation
        )
    
    @staticmethod
    @parameter_to_time_interval('time_interval')
    def from_to(
        time_interval: 'TimeInterval',
        start: Number,
        end: Number
    ) -> tuple[Union['TimeInterval', None], Union['TimeInterval', None], Union['TimeInterval', None], int]:
        """
        Cut a segment from the given `start` to the also provided
        `end` time moments of the `time_interval` passed as
        parameter.

        This method will return a tuple of 3 elements including the
        segments created by cutting this time interval in the order
        they were generated, but also having the 4th element always
        as the index of the one specifically requested by the user.
        The tuple will include all the segments at the begining and
        the rest will be None (unless the 4th one, which is the
        index).

        Examples below:
        - A time interval of `[2, 5)` cut with `start=3` and `end=4`
        will generate `((2, 3), (3, 4), (4, 5), 1)`.
        - A time interval of `[2, 5)` cut with `start=2` and `end=4`
        will generate `((2, 4), (4, 5), None, 0)`.
        - A time interval of `[2, 5)` cut with `start=4` and `end=5`
        will generate `((2, 4), (4, 5), None, 1)`.
        - A time interval of `[2, 5)` cut with `start=2` and `end=5`
        will generate `((2, 5), None, None, 0)`.

        As you can see, the result could be the same in different
        situations, but it's up to you (and the specific method in
        which you are calling to this one) to choose the tuple you
        want to return.
        """
        _validate_time_interval_current_limits(time_interval, start)
        _validate_time_interval_current_limits(time_interval, end)

        return (
            # TODO: What about this case, should we raise except (?)
            (
                time_interval.copy,
                None,
                None,
                0
            )
            if (
                start == time_interval.start and
                end == time_interval.end
            ) else
            (
                TimeInterval(
                    start = time_interval.start,
                    end = end,
                    start_limit = time_interval.start_limit,
                    end_limit = time_interval.end_limit,
                    fps = time_interval.fps
                ),
                TimeInterval(
                    start = end,
                    end = time_interval.end,
                    start_limit = time_interval.start_limit,
                    end_limit = time_interval.end_limit,
                    fps = time_interval.fps
                ),
                None,
                0
            )
            if start == time_interval.start else
            (
                TimeInterval(
                    start = time_interval.start,
                    end = start,
                    start_limit = time_interval.start_limit,
                    end_limit = time_interval.end_limit,
                    fps = time_interval.fps
                ),
                TimeInterval(
                    start = start,
                    end = time_interval.end,
                    start_limit = time_interval.start_limit,
                    end_limit = time_interval.end_limit,
                    fps = time_interval.fps
                ),
                None,
                1
            )
            if end == time_interval.end else
            (
                TimeInterval(
                    start = time_interval.start,
                    end = start,
                    start_limit = time_interval.start_limit,
                    end_limit = time_interval.end_limit,
                    fps = time_interval.fps
                ),
                TimeInterval(
                    start = start,
                    end = end,
                    start_limit = time_interval.start_limit,
                    end_limit = time_interval.end_limit,
                    fps = time_interval.fps
                ),
                TimeInterval(
                    start = end,
                    end = time_interval.end,
                    start_limit = time_interval.start_limit,
                    end_limit = time_interval.end_limit,
                    fps = time_interval.fps
                ),
                1
            )
        )
    
    @staticmethod
    @parameter_to_time_interval('time_interval')
    def split(
        time_interval: TimeInterval,
        t: Number,
    ) -> tuple[TimeInterval, TimeInterval]:
        """
        Split the interval at the provided `t` time moment and
        get the 2 new time intervals as a result (as a tuple).

        This method will raise an exception if the `t` value 
        provided is a limit value (or above).

        Examples below:
        - A time interval of `[2, 5)` cut with `t=3` will generate
        `((2, 3), (3, 5))`.
        - A time interval of `[2, 5)` cut with `t=4` will generate
        `((2, 4), (4, 5))`.
        - A time interval of `[2, 5)` cut with `t>=5` will raise
        exception.
        - A time interval of `[2, 5)` cut with `t<=2` will raise
        exception.
        """
        if (
            t <= time_interval.start or
            t >= time_interval.end
        ):
            raise Exception('The "t" value provided is not a valid value as it is a limit (or more than a limit).')
        
        return (
            TimeInterval(
                start = time_interval.start,
                end = t,
                start_limit = time_interval.start_limit,
                end_limit = time_interval.end_limit,
                fps = time_interval.fps
            ),
            TimeInterval(
                start = t,
                end = time_interval.end,
                start_limit = time_interval.start_limit,
                end_limit = time_interval.end_limit,
                fps = time_interval.fps
            )
        )
    
# TODO: Mix this class with the cutter and make single
# methods able to extend or cut based on if the variation
# is positive or negative
class TimeIntervalExtender:
    """
    Class to wrap the functionality related to extending
    """

    @staticmethod
    @parameter_to_time_interval('time_interval')
    def extend_end(
        time_interval: 'TimeInterval',
        t_variation: Number
    ):
        """
        Extend the end of the given `time_interval` the `t_variation`
        amount of seconds provided.
        """
        ParameterValidator.validate_mandatory_positive_number('t_variation', t_variation, do_include_zero = False)

        return TimeIntervalExtender.extend_end_to(
            time_interval = time_interval,
            t = time_interval.end + t_variation
        )
    
    @staticmethod
    @parameter_to_time_interval('time_interval')
    def extend_end_to(
        time_interval: 'TimeInterval',
        t: Number
    ):
        """
        Extend the end of the given `time_interval` the to the `t`
        time moment provided.
        """
        _validate_time_interval_original_limits(time_interval, t)
        
        if t < time_interval.end:
            raise Exception('The "t" parameter provided is lower than the current time interval `end` and this method is to extend it.')
        
        return TimeInterval(
            start = time_interval.start,
            end = t,
            start_limit = time_interval.start_limit,
            end_limit = time_interval.end_limit,
            fps = time_interval.fps
        )
    
    @staticmethod
    @parameter_to_time_interval('time_interval')
    def extend_start(
        time_interval: 'TimeInterval',
        t_variation: Number
    ):
        """
        Extend the start of the given `time_interval` the `t_variation`
        amount of seconds provided if the new `start` is greater than
        the `limit` provided and than the original (and min) `start`
        value of the time interval.
        """
        ParameterValidator.validate_mandatory_positive_number('t_variation', t_variation, do_include_zero = False)

        return TimeIntervalExtender.extend_start_to(
            time_interval = time_interval,
            t = time_interval.start - t_variation
        )
    
    @staticmethod
    @parameter_to_time_interval('time_interval')
    def extend_start_to(
        time_interval: 'TimeInterval',
        t: Number
    ):
        """
        Extend the start of the given `time_interval` the to the `t`
        time moment provided.
        """
        _validate_time_interval_original_limits(time_interval, t)
        
        if t > time_interval.start:
            raise Exception('The "t" parameter provided is greater than the current time interval `start` and this method is to extend it.')
        
        return TimeInterval(
            start = t,
            end = time_interval.end,
            start_limit = time_interval.start_limit,
            end_limit = time_interval.end_limit,
            fps = time_interval.fps
        )
    
def _validate_time_interval_original_limits(
    time_interval: TimeInterval,
    t: Number
) -> None:
    """
    *For internal use only*

    This method will raise an exception if the `t` time moment
    parameter value provided is out of the `time_interval` 
    original limits.

    TODO: How and where to put this (?)
    """
    if (
        t < time_interval.start_limit or
        t > time_interval.end_limit
    ):
        raise Exception(f'The "t" parameter value provided ({str(float(t))}) is out of the time interval limits (min and max) [{str(float(time_interval.start_limit))}, {str(float(time_interval.end_limit))}].')
                        
def _validate_time_interval_current_limits(
    time_interval: TimeInterval,
    t: Number
) -> None:
    """
    *For internal use only*

    This method will raise an exception if the `t` time moment
    parameter value provided is out of the `time_interval` 
    current limits (current `start` and `end`).

    This method is useful when we are cutting or splitting the
    time interval so the parameter value must be always within
    the current time range.

    TODO: How and where to put this (?)
    """
    if (
        t < time_interval.start or
        t > time_interval.end
    ):
        raise Exception(f'The "t" parameter value provided ({str(float(t))}) is out of the time interval current limits [{str(float(time_interval.start))}, {str(float(time_interval.end))}].')
    