#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2017 Matthew Stone <mstone5@mgh.harvard.edu>
# Distributed under terms of the MIT license.

"""
Standardize a VCF of SV calls.

Each record corresponds to a single SV breakpoint and will have the following
INFO fields, with specified constraints:
  SVTYPE:  SV type [DEL,DUP,INV,BND]
  CHR2:    Secondary chromosome [Must be lexicographically greater than CHROM]
  END:     SV end position (or position on CHR2 in translocations)
  STRANDS: Breakpoint strandedness [++,+-,-+,--]
  SVLEN:   SV length (-1 if translocation)
"""


def standardize_vcf(raw_vcf, std_vcf):
    """
    Iterator over the construction of new standardized records.

    Arguments
    ---------
    raw_vcf : pysam.VariantFile
        Input VCF.
    std_vcf : pysam.VariantFile
        Output VCF. Required to construct new VariantRecords.

    Yields
    ------
    std_rec : pysam.VariantRecord
        Standardized VCF record.
    """
    for raw_rec in raw_vcf:
        std_rec = std_vcf.new_record()
        std_rec = standardize_record(raw_rec, std_rec)
        yield std_rec


def standardize_record(raw_rec, std_rec):
    """
    Copies basic record data and standardizes INFO/FORMAT fields.

    Arguments
    ---------
    raw_rec : pysam.VariantRecord
        VCF record to standardize.
    std_rec : pysam.VariantRecord
        Empty VariantRecord constructed from new VariantFile.

    Returns
    -------
    std_rec : pysam.VariantRecord
        New VariantRecord with standardized data filled in.
    """

    # Copy basic record data
    std_rec.chrom = raw_rec.chrom
    std_rec.pos = raw_rec.pos
    std_rec.id = raw_rec.id
    std_rec.ref = raw_rec.ref
    std_rec.alts = raw_rec.alts

    # Strip filters
    std_rec.filter.add('PASS')

    # Copy defined INFO fields
    std_rec.info['SVTYPE'] = raw_rec.info['SVTYPE']
    std_rec.info['CHR2'] = raw_rec.chrom
    std_rec.info['END'] = raw_rec.pos + 1
    std_rec.info['SVLEN'] = 0
    std_rec.info['SOURCE'] = 'source'

    # Add per-sample formats
    for sample in raw_rec.samples:
        std_rec.samples[sample]['GT'] = raw_rec.samples[sample]['GT']

    return std_rec
