"""Regression checks for the data contract and the fail-fast training gate."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pandas as pd
import train
from validate_data import validation_result


class ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clean = pd.read_csv(train.DATA_PATH)

    def failures(self, df, minimum=1000):
        result = validation_result(df, minimum)
        return {r.expectation_config.kwargs.get('column', '(table)')
                for r in result.results if not r.success}

    def test_clean(self):
        self.assertEqual(self.failures(self.clean), set())

    def test_weak_income_check_misses_positive_unit_error(self):
        df=self.clean.copy(); df.loc[0,'annual_income']=17.59
        self.assertEqual(self.failures(df, 0), set())
        self.assertEqual(self.failures(df), {'annual_income'})

    def test_category_and_income_fail_together(self):
        df=self.clean.copy(); df.loc[0,'annual_income']=17.59
        df.loc[0,'employment_type']='contractor'
        self.assertEqual(self.failures(df), {'annual_income','employment_type'})

    def test_required_age_and_table_schema(self):
        df=self.clean.copy(); df.loc[0,'age']=float('nan');df['unexpected']=1
        self.assertEqual(self.failures(df), {'age','(table)'})

    def test_other_ranges_and_categories(self):
        df=self.clean.copy();df.loc[0,'age']=101
        df.loc[0,'home_ownership']='unknown';df.loc[0,'defaulted']=2
        self.assertEqual(self.failures(df), {'age','home_ownership','defaulted'})

    def test_gate_never_builds_or_fits_on_invalid_data(self):
        df=self.clean.copy();df.loc[0,'annual_income']=17.59
        with tempfile.TemporaryDirectory() as tmp:
            csv=Path(tmp)/'bad.csv';df.to_csv(csv,index=False)
            with patch.object(train,'DATA_PATH',str(csv)), \
                 patch.object(train,'load_data') as load, \
                 patch.object(train,'GridSearchCV') as grid, \
                 patch.object(train.mlflow,'start_run') as run, \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(train.main(),1)
                load.assert_not_called();grid.assert_not_called();run.assert_not_called()

    def test_stale_pointer_never_starts_grid_search(self):
        with patch.object(train,'get_data_hash',return_value='0'*32), \
             patch.object(train,'GridSearchCV') as grid, \
             patch.object(train.mlflow,'start_run') as run, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(train.main(),1)
            grid.assert_not_called();run.assert_not_called()


if __name__=='__main__':
    unittest.main(verbosity=2)
