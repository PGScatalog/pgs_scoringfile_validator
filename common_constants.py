SNP_DSET = 'rsID'
CHR_DSET = 'chr_name'
BP_DSET = 'chr_position'
EFFECT_DSET = 'effect_allele'
OTH_DSET = 'other_allele'
EFFECT_WEIGHT_DSET = 'effect_weight'
LOCUS_DSET ='locus_name'
OR_DSET = 'OR'
HR_DSET = 'HR'
BETA_DSET = 'beta'
FREQ_DSET = 'allelefrequency_effect'
FLAG_INTERACTION_DSET = 'is_interaction'
FLAG_RECESSIVE_DSET = 'is_recessive'
FLAG_HAPLOTYPE_DSET = 'is_haplotype'
FLAG_DIPLOTYPE_DSET = 'is_diplotype'
METHOD_DSET = 'imputation_method'
SNP_DESC_DSET = 'variant_description'
INCLUSION_DSET = 'inclusion_criteria'
DOSAGE_0_WEIGHT = 'dosage_0_weight'
DOSAGE_1_WEIGHT = 'dosage_1_weight'
DOSAGE_2_WEIGHT = 'dosage_2_weight'

DSET_TYPES = {SNP_DSET: str, CHR_DSET: str, BP_DSET: int, EFFECT_DSET: str, OTH_DSET: str,
              EFFECT_WEIGHT_DSET: float, LOCUS_DSET: str, OR_DSET: float, HR_DSET: float, BETA_DSET: float, FREQ_DSET: float,
              FLAG_INTERACTION_DSET: str, FLAG_RECESSIVE_DSET: str, FLAG_HAPLOTYPE_DSET: str, FLAG_DIPLOTYPE_DSET: str,
              METHOD_DSET: str, SNP_DESC_DSET: str, INCLUSION_DSET: str, DOSAGE_0_WEIGHT: float, DOSAGE_1_WEIGHT: float, DOSAGE_2_WEIGHT: float} #,

TO_DISPLAY_ORDER = [ SNP_DSET, CHR_DSET, BP_DSET, EFFECT_DSET, OTH_DSET, EFFECT_WEIGHT_DSET, LOCUS_DSET, FREQ_DSET, OR_DSET, HR_DSET, BETA_DSET]