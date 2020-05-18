import sys
import csv
sys.path.insert(0,'../../')
sys.path.insert(0,'../')
from common_constants import *

csv.field_size_limit(sys.maxsize)

header_mapper = {

    # Variant ID
    # ==========
    'variant_id': [
        'snp',
        '#SNP',
        'markername',
        'marker',
        'rs',
        'rsid',
        'rs_number',
        'rs_numbers',
        'assay_name',
        'id',
        'id_dbsnp49',
        'snp_rsid',
        'MARKER',
        'snpid',
        'oldid',
        'phase1_1kg_id',
        'SNP',
        'íd',
        'MarkerName',
        'rsID',
        'RSID',
        'MARKERNAME'
        ],

    # Chromosome
    # ==========
    'chromosome': [
        'chr',
        'chromosome',
        'chrom',
        'scaffold',
        'chr_build36',
        '#chrom',
        'CHR',
        'Chromosome'
        ],

    # Base pair location
    # ==================
    'base_pair_location': [
        'bp',
        'pos',
        'position',
        'phys_pos',
        'base_pair',
        'basepair',
        'base_pair_location',
        'pos_build36',
        'position_b37',
        'bp_hg19',
        'BP',
        'pos(b37)',
        'POS_b37',
        'POS' ,
        'Position',
        'position_build36',
        'Position_b37',
        'Position_hg19',
        'Pos_GRCh37',
        'chr_position'
        ],

    # Odds ratio
    # ==========
    'odds_ratio': [
        'or',
        'odds_ratio',
        'oddsratio',
        'bcac_icogs1_or',
        'OR'
        ],

    # Hazard ratio
    # ==========
    'hazard_ratio': [
        'hr',
        'hazard_ratio',
        'hazardatio',
        'HR'
        ],

    # Beta
    # ====
    'beta': [
        'b',
        'beta',
        'effects',
        'effect',
        'gwas_beta',
        'european_ancestry_beta_fix',
        'stdbeta',
        'bcac_onco_icogs_gwas_beta',
        'bcac_icogs1_risk_beta',
        'log_odds',
        'maineffects',
        'nbeta-clinical_c_k57',
        'Effect',
        'frequentist_add_beta_1:add/sle=1',
        'ALL.RANDOM.BETA',
        'BETA',
        'BETA_fathers_age_death',
        'BETA_parents_age_death',
        'BETA_top_1_percent',
        'Beta',
        'EFFECT',
        'EFFECT_A1'
        ],

    # Effect allele
    # =============
    'effect_allele': [
        'a1',
        'allele1',
        'allele_1',
        'effect_allele',
        'alt' ,
        'inc_allele',
        'ea',
        'alleleb',
        'allele_b',
        'effectallele',
        'a1',
        'alleleB',
        'A1',
        'Allele1',
        'alleleB',
        'ALLELE1',
        'EFF_ALLELE',
        'EffectAllele',
        'coded_allele',
        'Coded',
        'Effect-allele'
        ],

    # Other allele
    # ============
    'reference_allele': [
        'a2',
        'Allele2',
        'allele_2',
        'other_allele',
        'ref',
        'non_effect_allele',
        'dec_allele',
        'nea',
        'allelea',
        'allele_a',
        'reference_allele',
        'allele0',
        'referenceallele',
        'a0',
        'noneffect_allele',
        'alleleB',
        'A2',
        'alleleA',
        'ALLELE0',
        'allele2',
        'NONEFF_ALLELE',
        'OtherAllele',
        'non_coded_allele',
        'Non_coded',
        'Other-allele'
        ],

    # Effect allele frequency
    # =======================
    'effect_allele_frequency': [
        'maf',
        'eafcontrols',
        'frq',
        'ref_allele_frequency',
        'frq_u',
        'f_u',
        'effect_allele_freq',
        'effect_allele_frequency',
        'freq1',
        'alt_freq',
        'a1_af',
        'bcac_onco_icogs_gwas_eaf_controls',
        'bcac_icogs1_european_controls_eaf',
        'eaf_ukb',
        'allelefreq',
        'controls_maf',
        'effectAlleleFreq',
        'ALL.FREQ.VAR',
        'A1FREQ',
        'freqA1',
        'EAF_UKB',
        'EAF' ,
        'EFF_ALLELE_FREQ',
        'Freq',
        'FREQ_A1',
        'Coded_freq',
        'Effect-allele-frequency',
        'Freq1'
        ]
    }


CHR = CHR_DSET
BP = BP_DSET
VARIANT = SNP_DSET
OR_VAL = OR_DSET
HR_VAL = HR_DSET
BETA = BETA_DSET
CHR_BP = 'chr_bp'
EFFECT_ALLELE = EFFECT_DSET
REF_ALLELE = REF_DSET
FREQ_ALLELE = FREQ_DSET
EFFECT_WEIGHT = EFFECT_WEIGHT_DSET
LOCUS_NAME = LOCUS_DSET

known_header_transformations = {

    # variant id
    'snp': VARIANT,
    '#SNP': VARIANT,
    'markername': VARIANT,
    'marker': VARIANT,
    'rs': VARIANT,
    'rsid': VARIANT,
    'rs_number': VARIANT,
    'rs_numbers': VARIANT,
    'assay_name': VARIANT,
    'id': VARIANT,
    'id_dbsnp49': VARIANT,
    'snp_rsid': VARIANT,
    'MARKER': VARIANT,
    'snpid':'snp',
    'oldid':'snp',
    'phase1_1kg_id':'snp',
    'SNP': VARIANT,
    'íd': VARIANT,
    'MarkerName': VARIANT,
    'rsID': VARIANT,
    'RSID': VARIANT,
    'MARKERNAME': VARIANT,
    # chromosome
    'chr': CHR,
    'chromosome': CHR,
    'chrom': CHR,
    'scaffold': CHR,
    'chr_build36': CHR,
    '#chrom': CHR,
    'CHR': CHR,
    'Chromosome': CHR,
    # base pair location
    'bp': BP,
    'pos': BP,
    'position': BP,
    'phys_pos': BP,
    'base_pair': BP,
    'basepair': BP,
    'base_pair_location': BP,
    'pos_build36': BP,
    'position_b37': BP,
    'bp_hg19': BP,
    'BP': BP,
    'pos(b37)': BP,
    'POS_b37': BP,
    'POS' : BP,
    'Position': BP,
    'position_build36': BP,
    'Position_b37': BP,
    'Position_hg19': BP,
    'position_hg19': BP,
    # chromosome combined with base pair location
    'chr_pos' : CHR_BP,
    'chrpos' : CHR_BP,
    'chr_position' : CHR_BP,
    'chrpos_b37' : CHR_BP,
    'chr_pos_b37' : CHR_BP,
    'chrpos_b36' : CHR_BP,
    'chr_pos_b36' : CHR_BP,
    'chrpos_b38' : CHR_BP,
    'chr_pos_b38' : CHR_BP,
    'chr_pos_(b36)' : CHR_BP,
    'chr_pos_(b37)' : CHR_BP,
    'chr_pos_(b38)' : CHR_BP,
    'Chr': CHR,
    # odds ratio
    'or': OR_VAL,
    'odds_ratio': OR_VAL,
    'oddsratio': OR_VAL,
    'bcac_icogs1_or': OR_VAL,
    'OR': OR_VAL,
    # hazard ratio
    'hr': HR_VAL,
    'hazard_ratio': HR_VAL,
    'hazardratio': HR_VAL,
    'HR': HR_VAL,
    # beta
    'b': BETA,
    'beta': BETA,
    'effects': BETA,
    'effect': BETA,
    'gwas_beta': BETA,
    'european_ancestry_beta_fix': BETA,
    'stdbeta': BETA,
    'bcac_onco_icogs_gwas_beta':'beta',
    'bcac_icogs1_risk_beta': BETA,
    'log_odds': BETA,
    'maineffects': BETA,
    'nbeta-clinical_c_k57': BETA,
    'Effect': BETA,
    'frequentist_add_beta_1:add/sle=1': BETA,
    'ALL.RANDOM.BETA': BETA,
    'BETA':'beta',
    'BETA_fathers_age_death': BETA,
    'BETA_parents_age_death': BETA,
    'BETA_top_1_percent': BETA,
    'Beta': BETA,
    'EFFECT': BETA,
    'EFFECT_A1': BETA,
    # effect allele
    'a1': EFFECT_ALLELE,
    'allele1': EFFECT_ALLELE,
    'allele_1': EFFECT_ALLELE,
    'effect_allele': EFFECT_ALLELE,
    'alt' : EFFECT_ALLELE,
    'inc_allele': EFFECT_ALLELE,
    'ea': EFFECT_ALLELE,
    'alleleb': EFFECT_ALLELE,
    'allele_b': EFFECT_ALLELE,
    'effectallele': EFFECT_ALLELE,
    'a1': EFFECT_ALLELE,
    'alleleB': EFFECT_ALLELE,
    'A1': EFFECT_ALLELE,
    'Allele1':'effect_allele',
    'alleleB': EFFECT_ALLELE,
    'ALLELE1': EFFECT_ALLELE,
    'EFF_ALLELE': EFFECT_ALLELE,
    'EffectAllele': EFFECT_ALLELE,
    'coded_allele': EFFECT_ALLELE,
    'Coded': EFFECT_ALLELE,
    'Effect-allele': EFFECT_ALLELE,
    # other allele
    'a2': REF_ALLELE,
    'Allele2': REF_ALLELE,
    'allele_2': REF_ALLELE,
    'other_allele': REF_ALLELE,
    'ref': REF_ALLELE,
    'non_effect_allele': REF_ALLELE,
    'dec_allele': REF_ALLELE,
    'nea': REF_ALLELE,
    'allelea': REF_ALLELE,
    'allele_a': REF_ALLELE,
    'reference_allele': REF_ALLELE,
    'allele0': REF_ALLELE,
    'referenceallele': REF_ALLELE,
    'a0': REF_ALLELE,
    'noneffect_allele': REF_ALLELE,
    'alleleB': REF_ALLELE,
    'A2': REF_ALLELE,
    'alleleA': REF_ALLELE,
    'ALLELE0': REF_ALLELE,
    'allele2': REF_ALLELE,
    'NONEFF_ALLELE': REF_ALLELE,
    'OtherAllele': REF_ALLELE,
    'non_coded_allele': REF_ALLELE,
    'Non_coded': REF_ALLELE,
    'Other-allele': REF_ALLELE,
    # effect allele frequency
    'maf': FREQ_ALLELE,
    'eafcontrols': FREQ_ALLELE,
    'frq': FREQ_ALLELE,
    'ref_allele_frequency': FREQ_ALLELE,
    'frq_u': FREQ_ALLELE,
    'f_u': FREQ_ALLELE,
    'effect_allele_freq': FREQ_ALLELE,
    'effect_allele_frequency': FREQ_ALLELE,
    'freq1': FREQ_ALLELE,
    'alt_freq': FREQ_ALLELE,
    'a1_af': FREQ_ALLELE,
    'bcac_onco_icogs_gwas_eaf_controls': FREQ_ALLELE,
    'bcac_icogs1_european_controls_eaf': FREQ_ALLELE,
    'eaf_ukb': FREQ_ALLELE,
    'allelefreq': FREQ_ALLELE,
    'controls_maf': FREQ_ALLELE,
    'effectAlleleFreq': FREQ_ALLELE,
    'ALL.FREQ.VAR': FREQ_ALLELE,
    'A1FREQ': FREQ_ALLELE,
    'freqA1': FREQ_ALLELE,
    'EAF_UKB': FREQ_ALLELE,
    'EAF' : FREQ_ALLELE,
    'EFF_ALLELE_FREQ': FREQ_ALLELE,
    'Freq': FREQ_ALLELE,
    'FREQ_A1': FREQ_ALLELE,
    'Coded_freq': FREQ_ALLELE,
    'Effect-allele-frequency': FREQ_ALLELE,
    'Freq1': FREQ_ALLELE,
}

#CHR_BP = 'chr_bp'
#CHR = 'chr'
#BP = 'bp'
#VARIANT = 'snp'

DESIRED_HEADERS = {CHR, BP, VARIANT, OR_VAL, HR_VAL, BETA, CHR_BP, EFFECT_ALLELE, REF_ALLELE, FREQ_ALLELE, EFFECT_WEIGHT, LOCUS_NAME}

VALID_INPUT_HEADERS = set(known_header_transformations.values())

VALID_CHROMS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', 'X', 'Y', 'MT']


def get_row_count(file):
    with open(file, 'r') as f:
        return len(f.readlines())


def read_header(file):
    return set([clean_header(x.rstrip('\n')) for x in open(file).readline().split()])


def clean_header(header):
    return header.lower().replace('-', '_').replace('.', '_').replace('\n', '')


def refactor_header(header):
    header = [clean_header(h) for h in header]
    return [known_header_transformations[h] if h in known_header_transformations else h for h in header]


def mapped_headers(header):
    return {h: known_header_transformations[clean_header(h)] for h in header if clean_header(h) in known_header_transformations}


def get_csv_reader(csv_file):
    dialect = csv.Sniffer().sniff(csv_file.readline())
    csv_file.seek(0)
    return csv.reader(csv_file, dialect)


def get_filename(file):
    return file.split("/")[-1].split(".")[0]
