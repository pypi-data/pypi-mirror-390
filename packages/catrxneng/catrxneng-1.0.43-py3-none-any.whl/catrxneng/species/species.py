class Species:
    CLASS = "species"
    C_ATOMS = 0
    H_ATOMS = 0
    O_ATOMS = 0
    N_ATOMS = 0
    MOL_WEIGHT = 0.0
    NIST_THERMO_PARAMS: list

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def _get_thermo_params(cls, T):
        for thermo_params in cls.NIST_THERMO_PARAMS:
            if thermo_params["min_temp_K"] <= T.K <= thermo_params["max_temp_K"]:
                return thermo_params
        raise ValueError(
            f"Temperature outside range for {cls.__name__} thermodynamic parameters."
        )
