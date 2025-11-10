from typing_extensions import override

from cartographer.adapters.klipper_like.axis_twist_compensation import KlipperLikeAxisTwistCompensationAdapter


class KlipperAxisTwistCompensationAdapter(KlipperLikeAxisTwistCompensationAdapter):
    @override
    def get_z_compensation_value(self, *, x: float, y: float) -> float:
        pos = [x, y, 0]
        self.printer.send_event("probe:update_results", pos)
        return pos[2]
