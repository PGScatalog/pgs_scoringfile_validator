import unittest
import shutil
import os
import sys
import tests.prep_tests as prep
import validate.validator as v
from validate.common_constants import *
import tests.test_values as test_arrays


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.test_storepath = "./tests/data"
        os.makedirs(self.test_storepath, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_storepath)

    def test_validate_good_file_extension(self):
        test_filepath = os.path.join(self.test_storepath, "test_file.tsv.gz")
        validator = v.Validator(test_filepath, "pgs-upload", logfile=test_filepath + ".LOG")
        valid_ext = validator.validate_file_extension()
        self.assertTrue(valid_ext)
        # alternative
        test_filepath = os.path.join(self.test_storepath, "test_file.csv.gz")
        validator = v.Validator(test_filepath, "pgs-upload", logfile=test_filepath + ".LOG")
        valid_ext = validator.validate_file_extension()
        self.assertTrue(valid_ext)

    def test_validate_bad_file_extension(self):
        test_filepath = os.path.join(self.test_storepath, "test_file.zip")
        validator = v.Validator(test_filepath, "pgs-upload", logfile=test_filepath + ".LOG")
        valid_ext = validator.validate_file_extension()
        self.assertFalse(valid_ext)

    def test_validate_good_file_headers(self):
        test_filepath = os.path.join(self.test_storepath, "test_file.tsv")
        setup_file = prep.SSTestFile()
        setup_file.prep_test_file()
        validator = v.Validator(test_filepath, "pgs-upload", logfile=test_filepath + ".LOG")
        valid_headers = validator.validate_headers()
        self.assertTrue(valid_headers)

    def test_validate_file_headers_missing_snp(self):
        test_filepath = os.path.join(self.test_storepath, "test_file.tsv")
        setup_file = prep.SSTestFile()
        setup_file.set_test_data_dict()
        setup_file.test_data_dict.pop(SNP_DSET) # remove a snp field
        setup_file.prep_test_file()
        validator = v.Validator(test_filepath, "pgs-upload", logfile=test_filepath + ".LOG")
        valid_headers = validator.validate_headers()
        self.assertTrue(valid_headers)

    def test_validate_file_headers_missing_pos(self):
        test_filepath = os.path.join(self.test_storepath, "test_file.tsv")
        setup_file = prep.SSTestFile()
        setup_file.set_test_data_dict()
        setup_file.test_data_dict.pop(CHR_DSET) # remove the chr field
        setup_file.test_data_dict.pop(BP_DSET)  # remove the pos field
        setup_file.prep_test_file()
        validator = v.Validator(test_filepath, "pgs-upload", logfile=test_filepath + ".LOG")
        valid_headers = validator.validate_headers()
        self.assertTrue(valid_headers)

    def test_validate_file_headers_missing_snp_and_pos(self):
        test_filepath = os.path.join(self.test_storepath, "test_file.tsv")
        setup_file = prep.SSTestFile()
        setup_file.set_test_data_dict()
        setup_file.test_data_dict.pop(SNP_DSET) # remove a snp field
        setup_file.test_data_dict.pop(CHR_DSET) # remove the chr field
        setup_file.test_data_dict.pop(BP_DSET)  # remove the pos field
        setup_file.prep_test_file()
        validator = v.Validator(test_filepath, "pgs-upload", logfile=test_filepath + ".LOG")
        valid_headers = validator.validate_headers()
        self.assertFalse(valid_headers)

    def test_validate_bad_file_headers(self):
        test_filepath = os.path.join(self.test_storepath, "test_file.tsv")
        setup_file = prep.SSTestFile()
        setup_file.set_test_data_dict()
        setup_file.test_data_dict.pop(EFFECT_DSET) # remove a mandatory field
        setup_file.prep_test_file()
        validator = v.Validator(test_filepath, "pgs-upload", logfile=test_filepath + ".LOG")
        valid_headers = validator.validate_headers()
        self.assertFalse(valid_headers)

    def test_validate_bad_file_headers_missing_effect(self):
        test_filepath = os.path.join(self.test_storepath, "test_file.tsv")
        setup_file = prep.SSTestFile()
        setup_file.set_test_data_dict()
        setup_file.test_data_dict.pop(EFFECT_WEIGHT_DSET) # remove effect_weight field
        setup_file.test_data_dict.pop(OR_DSET)            # remove odds ratio field
        setup_file.test_data_dict.pop(HR_DSET)            # remove hazard ratio field
        setup_file.prep_test_file()
        validator = v.Validator(test_filepath, "pgs-upload", logfile=test_filepath + ".LOG")
        valid_headers = validator.validate_headers()
        self.assertFalse(valid_headers)

    def test_validate_good_file_data(self):
        test_filepath = os.path.join(self.test_storepath, "test_file.tsv")
        logfile=test_filepath.replace('tsv', 'LOG')
        setup_file = prep.SSTestFile()
        setup_file.prep_test_file()
        validator = v.Validator(test_filepath, "pgs-upload", logfile=logfile)
        valid_data = validator.validate_data()
        self.assertTrue(valid_data)

    def test_validate_bad_snp_file_data(self):
        test_filename = "bad_snp.tsv"
        test_filepath = os.path.join(self.test_storepath, test_filename)
        logfile=test_filepath.replace('tsv', 'LOG')
        setup_file = prep.SSTestFile(filename=test_filename)
        setup_file.set_test_data_dict()
        setup_file.test_data_dict[SNP_DSET] = ["invalid", 123, "1_1234_A_G", "ss151232"] # set bad snps
        setup_file.prep_test_file()
        validator = v.Validator(file=test_filepath, filetype="pgs-upload", logfile=logfile)
        valid_data = validator.validate_data()
        self.assertEqual(len(validator.bad_rows), 4)
        self.assertFalse(valid_data)

    def test_validate_bad_snp_and_no_pos_file_data(self):
        test_filename = "bad_snp_no_pos.tsv"
        test_filepath = os.path.join(self.test_storepath, test_filename)
        logfile=test_filepath.replace('tsv', 'LOG')
        setup_file = prep.SSTestFile(filename=test_filename)
        setup_file.set_test_data_dict()
        setup_file.test_data_dict[SNP_DSET] = ["invalid", "rs123", "1_1234_A_G", "ss151232"] # set bad snps
        setup_file.test_data_dict[BP_DSET] = [None, 123, "NA", None] # only one good row
        setup_file.prep_test_file()
        validator = v.Validator(file=test_filepath, filetype="pgs-upload", logfile=logfile)
        valid_data = validator.validate_data()
        self.assertEqual(len(validator.bad_rows), 3)
        self.assertFalse(valid_data)

    def test_validate_bad_chr_file_data(self):
        test_filename = "bad_chr.tsv"
        test_filepath = os.path.join(self.test_storepath, test_filename)
        logfile=test_filepath.replace('tsv', 'LOG')
        setup_file = prep.SSTestFile(filename=test_filename)
        setup_file.set_test_data_dict()
        setup_file.test_data_dict[CHR_DSET] = [1, 123, "CHR1", "X"] # set 2 bad chrs
        setup_file.prep_test_file()
        validator = v.Validator(file=test_filepath, filetype="pgs-upload", logfile=logfile)
        valid_data = validator.validate_data()
        self.assertEqual(len(validator.bad_rows), 2)
        self.assertFalse(valid_data)

    def test_validate_bad_chr_and_no_snp_file_data(self):
        test_filename = "bad_chr_no_snp.tsv"
        test_filepath = os.path.join(self.test_storepath, test_filename)
        logfile=test_filepath.replace('tsv', 'LOG')
        setup_file = prep.SSTestFile(filename=test_filename)
        setup_file.set_test_data_dict()
        setup_file.test_data_dict[CHR_DSET] = [1, 123, "CHR1", "X"] # set 2 bad chrs
        setup_file.test_data_dict[SNP_DSET] = ["invalid", 123, "rs1234", "rs151"] # set only one good row
        setup_file.prep_test_file()
        validator = v.Validator(file=test_filepath, filetype="pgs-upload", logfile=logfile)
        valid_data = validator.validate_data()
        self.assertEqual(len(validator.bad_rows), 3)
        self.assertFalse(valid_data)

    def test_validate_bad_bp_file_data(self):
        test_filename = "bad_bp.tsv"
        test_filepath = os.path.join(self.test_storepath, test_filename)
        logfile=test_filepath.replace('tsv', 'LOG')
        setup_file = prep.SSTestFile(filename=test_filename)
        setup_file.set_test_data_dict()
        setup_file.test_data_dict[BP_DSET] = [1, 1234567890, "CHR1_122334", 123245] # set 2 bad bps
        setup_file.prep_test_file()
        validator = v.Validator(file=test_filepath, filetype="pgs-upload", logfile=logfile)
        valid_data = validator.validate_data()
        self.assertEqual(len(validator.bad_rows), 2)
        self.assertFalse(valid_data)

    def test_validate_bad_bp_and_no_snp_file_data(self):
        test_filename = "bad_bp_no_snp.tsv"
        test_filepath = os.path.join(self.test_storepath, test_filename)
        logfile=test_filepath.replace('tsv', 'LOG')
        setup_file = prep.SSTestFile(filename=test_filename)
        setup_file.set_test_data_dict()
        setup_file.test_data_dict[BP_DSET] = [1, 1234567890, "CHR1_122334", 123245] # set 2 bad bps
        setup_file.test_data_dict[SNP_DSET] = ["invalid", 123, None, "rs1234"] # set so only one good row
        setup_file.prep_test_file()
        validator = v.Validator(file=test_filepath, filetype="pgs-upload", logfile=logfile)
        valid_data = validator.validate_data()
        self.assertEqual(len(validator.bad_rows), 3)
        self.assertFalse(valid_data)

    def test_validate_bad_optional_effect_weight_file_data(self):
        test_filename = "bad_weight.tsv"
        test_filepath = os.path.join(self.test_storepath, test_filename)
        logfile=test_filepath.replace('tsv', 'LOG')
        setup_file = prep.SSTestFile(filename=test_filename)
        setup_file.set_test_data_dict()
        setup_file.test_data_dict[EFFECT_WEIGHT_DSET] = [1.1232e-23, "invalid", 0.123, .3245] # set 1 bad bps
        setup_file.prep_test_file()
        validator = v.Validator(file=test_filepath, filetype="pgs-upload", logfile=logfile)
        valid_data = validator.validate_data()
        self.assertEqual(len(validator.bad_rows), 1)
        self.assertFalse(valid_data)

    def test_validate_bad_optional_odds_ratio_file_data(self):
        test_filename = "bad_odds.tsv"
        test_filepath = os.path.join(self.test_storepath, test_filename)
        logfile=test_filepath.replace('tsv', 'LOG')
        setup_file = prep.SSTestFile(filename=test_filename)
        setup_file.set_test_data_dict()
        setup_file.test_data_dict[OR_DSET] = [1.1232e-23, "invalid", 0.123, .3245] # set 1 bad bps
        setup_file.prep_test_file()
        validator = v.Validator(file=test_filepath, filetype="pgs-upload", logfile=logfile)
        valid_data = validator.validate_data()
        self.assertEqual(len(validator.bad_rows), 1)
        self.assertFalse(valid_data)

    def test_validate_bad_optional_hazard_ratio_file_data(self):
        test_filename = "bad_hazard.tsv"
        test_filepath = os.path.join(self.test_storepath, test_filename)
        logfile=test_filepath.replace('tsv', 'LOG')
        setup_file = prep.SSTestFile(filename=test_filename)
        setup_file.set_test_data_dict()
        setup_file.test_data_dict[HR_DSET] = [1.1232e-23, "invalid", 0.123, .3245] # set 1 bad bps
        setup_file.prep_test_file()
        validator = v.Validator(file=test_filepath, filetype="pgs-upload", logfile=logfile)
        valid_data = validator.validate_data()
        self.assertEqual(len(validator.bad_rows), 1)
        self.assertFalse(valid_data)

    def test_validate_bad_effect_allele_file_data(self):
        test_filename = "bad_effect.tsv"
        test_filepath = os.path.join(self.test_storepath, test_filename)
        logfile=test_filepath.replace('tsv', 'LOG')
        setup_file = prep.SSTestFile(filename=test_filename)
        setup_file.set_test_data_dict()
        setup_file.test_data_dict[EFFECT_DSET] = ['A', 'AGG', 'INS:T', 'd'] # set 2 bad alleles
        setup_file.prep_test_file()
        validator = v.Validator(file=test_filepath, filetype="pgs-upload", logfile=logfile)
        valid_data = validator.validate_data()
        self.assertEqual(len(validator.bad_rows), 2)
        self.assertFalse(valid_data)

    def test_validate_empty_snp_file_data(self):
        test_filename = "empty_snp.tsv"
        test_filepath = os.path.join(self.test_storepath, test_filename)
        logfile=test_filepath.replace('tsv', 'LOG')
        setup_file = prep.SSTestFile(filename=test_filename)
        setup_file.set_test_data_dict()
        setup_file.test_data_dict[SNP_DSET] = ["NA", None, None, None] # set bad snps
        setup_file.prep_test_file()
        validator = v.Validator(file=test_filepath, filetype="pgs-upload", logfile=logfile)
        valid_data = validator.validate_data()
        self.assertEqual(len(validator.bad_rows), 4)
        self.assertFalse(valid_data)

    def test_validate_empty_snp_no_pos_file_data(self):
        test_filename = "empty_snp_no_pos.tsv"
        test_filepath = os.path.join(self.test_storepath, test_filename)
        logfile=test_filepath.replace('tsv', 'LOG')
        setup_file = prep.SSTestFile(filename=test_filename)
        setup_file.set_test_data_dict()
        setup_file.test_data_dict[SNP_DSET] = ["NA", None, "1234", "rs1"] # set bad snps
        setup_file.test_data_dict[BP_DSET] = [None, 123, "NA", None] # only one good bp
        setup_file.prep_test_file()
        validator = v.Validator(file=test_filepath, filetype="pgs-upload", logfile=logfile)
        valid_data = validator.validate_data()
        self.assertEqual(len(validator.bad_rows), 4)
        self.assertFalse(valid_data)



if __name__ == '__main__':
    unittest.main()
