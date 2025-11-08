import pandas as pd
from suclepy.core.role_infer import RoleInfer

def test_role_infer():
    df = pd.DataFrame({
        "id_col": [1, 2, 3],
        "num_col": [1.1, 2.2, 3.3],
        "cat_col": ["a", "b", "c"],
        "date_col": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"])
    })

    role_infer = RoleInfer(df)
    roles = role_infer.run()

    assert roles["id_col"] == "id"
    assert roles["num_col"] == "numeric"
    assert roles["cat_col"] == "categorical"
    assert roles["date_col"] == "date"
