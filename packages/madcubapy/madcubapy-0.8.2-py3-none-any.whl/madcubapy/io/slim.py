# import astropy
import astropy
from astropy.table import Table
from astropy.table import Column
import numpy as np

from madcubapy.utils.numeric import _return_significant_value

__all__ = [
    'import_molecular_parameters_table',
    'format_molecular_parameters_columns',
    'output_latex_molecular_parameters_table',
]

def import_molecular_parameters_table(filein=None, format='ascii'):
    """Import a SLIM Molecular parameters table exported from MADCUBA as a
    `~astropy.table.Table`.

    Parameters
    ----------
    filein : `str` or `~pathlib.Path`
        File name of the exported MADCUBA transitions table.
    format : `str`
        File format exported by MADCUBA. Can be either 'ascii' or 'csv'.

    Returns
    -------
    table_out : `~astropy.table.Table`
        Molecular Parameters Table.

    """

    if format=='csv':
        table_in = Table.read(filein, format='csv', delimiter=',')
    elif format=='ascii':
        table_in = Table.read(filein, format='ascii', delimiter='\t')
    # Select subtable
    table_trim = table_in[
        "formula",
        "Comp.",
        "FWHM",
        "f_3",
        "delta_3",
        "VLSR_",
        "f_2",
        "delta_2",
        "logN|EM",
        "f",
        "delta",
        "Tex|Te*",
        "f_1",
        "delta_1",
        "Noise",
        "AutofitNoise",
        "UpperLimits",
        "AutofitTau",
        "Autofit",
        "Simulate",
        "IsUseAllSpecies",
        "ChangeSimulate",
        "UpperLimitsTex",
        "TMB",
        "ApplyAllSpecies",
        "ApplyOnlyCheck",
    ]
    # create indexes to help ordering later
    order_index = np.arange(len(table_trim))+1
    table_trim.add_column(order_index, name='Order_index', index=0)
    # Get unique rows from table
    table_out = astropy.table.unique(table_trim, keys=['formula', 'Comp.'],
                                     keep='first')
    table_out.sort('Order_index')  # may need to order by velocity after this
    # Create short names for molecules important for this work
    short_names = []
    for name in table_out['formula']:
        if name == 'PN,v=0-5,hfs':
            short_name = 'PN,hfs'
        elif name == 'PN,v=0-5':
            short_name = 'PN'
        elif name == 'PO,v=0':
            short_name = 'PO'
        elif name == 'SO,v=0':
            short_name = 'SO'
        elif name == 'SO2,v=0':
            short_name = 'SO2'
        elif name == 'SiO,v=0-10':
            short_name = 'SiO'
        elif name == 'CH3OH,vt=0-2':
            short_name = 'CH3OH'
        elif name == 'CH2DOH':
            short_name = 'CH2DOH'
        elif name == 'CHD2OH,vt=0':
            short_name = 'CHD2OH'
        elif name == 'CH3OCH3,v=0':
            short_name = 'CH3OCH3'
        elif name == 'CH3OCHO':
            short_name = 'CH3OCHO'
        elif name == 't-HC-13-OOH':
            short_name = 't-HC-13-OOH'
        else:
            short_name = f'DEL---{name}'
        short_names.append(short_name)
    # Create latex labels
    label_names = []
    for name in table_out['formula']:
        if name == 'PN,v=0-5,hfs':
            label_name = 'PN (HFS)'
        elif name == 'PN,v=0-5':
            label_name = 'PN'
        elif name == 'PO,v=0':
            label_name = 'PO'
        elif name == 'SO,v=0':
            label_name = 'SO'
        elif name == 'SO2,v=0':
            label_name = 'SO$_{2}$'
        elif name == 'SiO,v=0-10':
            label_name = 'SiO'
        elif name == 'CH3OH,vt=0-2':
            label_name = 'CH$_{3}$OH'
        elif name == 'CH2DOH':
            label_name = 'CH$_{2}$DOH'
        elif name == 'CHD2OH,vt=0':
            label_name = 'CHD$_{2}$OH'
        elif name == 'CH3OCH3,v=0':
            label_name = 'CH$_{3}$OCH$_{3}$'
        elif name == 'CH3OCHO':
            label_name = 'CH$_{3}$OCHO'
        elif name == 't-HC-13-OOH':
            label_name = '$t$-HC$^{13}$OOH'
        else:
            label_name = name
        label_names.append(label_name)
    # Rename table columns to be the same as SLIM Tables
    table_out['formula'].name = 'Formula'
    table_out['Comp.'].name = 'C'
    table_out['FWHM'].name = 'Width'
    table_out['delta_3'].name = 'delta Width'
    table_out['f_3'].name = 'f Width'
    table_out['VLSR_'].name = 'Velocity'
    table_out['delta_2'].name = 'delta Velocity'
    table_out['f_2'].name = 'f Velocity'
    table_out['logN|EM'].name = 'N/EM'
    table_out['delta'].name = 'delta N/EM'
    table_out['f'].name = 'f N/EM'
    table_out['Tex|Te*'].name = 'Tex/Te'
    table_out['delta_1'].name = 'delta Tex/Te'
    table_out['f_1'].name = 'f Tex/Te'
    table_out.add_column(label_names, name='Label', index=1)
    table_out.add_column(short_names, name='Formula_short', index=2)

    return table_out


def format_molecular_parameters_columns(table):
    """Add new columns to a Molecular Parameters Table with LaTeX formatted
    strings for the physical parameters column density, excitation temperature,
    width, and velocity; using significant values and previous related values
    from other components or molecules.

    Parameters
    ----------
    table : `~astropy.table.Table`
        Input Molecular Parameters Table.

    Returns
    -------
    table_out : `~astropy.table.Table`
        Formatted Molecular Parameters Table.

    """

    formattable_params = ['N/EM', 'Tex/Te', 'Velocity', 'Width']

    table_out = table.copy(copy_data=True)

    for param in formattable_params:
        # Prepare column names
        value_col = param
        delta_col = f'delta {param}'
        f_col = f'f {param}'

        # Create new formatted column
        new_column_empty_vals = np.array(["--" for row in table_out], dtype="U50")
        formatted_col = f'formatted {param}'
        new_column = Column(new_column_empty_vals, name=formatted_col)
        pos = table_out.colnames.index(delta_col) + 1
        if formatted_col in table_out.colnames:
            table_out.remove_column(formatted_col)
        table_out.add_column(new_column, index=pos)

        # Special case. For column density just measure significant values
        if param == 'N/EM':
            for row in table_out:
                value = (10**row[value_col]) / (10**13)
                unc = (10**row[delta_col]) / (10**13)
                if row['Autofit'] == 'true':
                    dummy, unc_formatted, round_num = _return_significant_value(unc)
                    value_formatted = round(value, round_num)
                    row[formatted_col] = f"{value_formatted} +/- {unc_formatted}"
                elif row['UpperLimits'] == 'true':
                    dummy, value_formatted, round_num = _return_significant_value(value)
                    row[formatted_col] = f"<{value_formatted}"
                else:
                    row[formatted_col] = f"Norun-{value}"
            continue
        
        # first run: format only autofit rows
        for row in table_out:
            if row['Autofit'] == 'true' and row[f_col] == 'false':
                unc = row[delta_col]
                dummy, unc_formatted, round_num = _return_significant_value(unc)
                value_formatted = round(row[value_col], round_num)
                row[formatted_col] = f"{value_formatted} +/- {unc_formatted}"

        # second run: format inside molecule groups that have at last one component of the same value and one autofit component
        formula_groups = table_out.group_by("Formula")
        for formula_group in formula_groups.groups:
            formula = formula_group["Formula"][0]
            # skip groups with one row
            if len(formula_group) == 1:
                continue
            # skip if there are no autofitted and formatted values in group
            formatted_filter = (formula_group["Autofit"] == 'true') & (formula_group[formatted_col] != '--')
            unformatted_filter = formula_group[formatted_col] == '--'
            if len(formula_group[formatted_filter]) == 0:
                continue
            for row in formula_group[unformatted_filter]:
                comp = row["C"]
                found_value_filter = np.isclose(formula_group[value_col], row[value_col])
                if len(formula_group[formatted_filter & found_value_filter]) == 0:
                    continue
                elif len(formula_group[formatted_filter & found_value_filter]) == 1:
                    found_comp_row = formula_group[formatted_filter & found_value_filter][0]
                    unc = found_comp_row[delta_col]
                    dummy, unc_formatted, round_num = _return_significant_value(unc)
                    value_formatted = round(row[value_col], round_num)
                    # cannot modify directly the row from a masked table. It is a mini table copied from the main one
                    # row[formatted_col] = f"{value_formatted}"
                    # use the index value instead
                    index = row["Order_index"] - 1
                    table_out[index][formatted_col] = f"{value_formatted}"
                else:
                    row[formatted_col] = "error"
                    # FIND OUT WHAT CAN I DO HERE. THE OTHER VERSION COULD USE OLDER CODE FOR THIS PART


        # third run: format comps that have same value and autofit (and formatted value) in the same comp of other molecules
        comp_groups = table_out.group_by("C")
        for comp_group in comp_groups.groups:
            comp = comp_group["C"][0]
            # skip groups with one row
            if len(comp_group) == 1:
                continue
            # skip if there are no autofitted and formatted values in group
            formatted_filter = (comp_group["Autofit"] == 'true') & (comp_group[formatted_col] != '--')
            unformatted_filter = comp_group[formatted_col] == '--'
            if len(comp_group[formatted_filter]) == 0:
                continue
            for row in comp_group[unformatted_filter]:
                formula = row['Formula']
                found_value_filter = np.isclose(comp_group[value_col], row[value_col])
                if len(comp_group[formatted_filter & found_value_filter]) == 0:
                    continue
                elif len(comp_group[formatted_filter & found_value_filter]) == 1:
                    found_comp_row = comp_group[formatted_filter & found_value_filter][0]
                    unc = found_comp_row[delta_col]
                    dummy, unc_formatted, round_num = _return_significant_value(unc)
                    value_formatted = round(row[value_col], round_num)
                    index = row["Order_index"] - 1
                    table_out[index][formatted_col] = f"{value_formatted}"
                else:
                    row[formatted_col] = "error"

        # fourth run: format inside molecule groups that have at last one component of the same value
        formula_groups = table_out.group_by("Formula")
        for formula_group in formula_groups.groups:
            formula = formula_group["Formula"][0]
            # skip groups with one row
            if len(formula_group) == 1:
                continue
            # skip if there are no autofitted and formatted values in group
            formatted_filter = formula_group[formatted_col] != '--'
            unformatted_filter = formula_group[formatted_col] == '--'
            if len(formula_group[formatted_filter]) == 0:
                continue
            for row in formula_group[unformatted_filter]:
                comp = row["C"]
                found_value_filter = np.isclose(formula_group[value_col], row[value_col])
                if len(formula_group[formatted_filter & found_value_filter]) == 0:
                    continue
                elif len(formula_group[formatted_filter & found_value_filter]) == 1:
                    found_comp_row = formula_group[formatted_filter & found_value_filter][0]
                    # Now there is no need to get the significant values. THis is straight copy paste like I did in MADCUBA
                    index = row["Order_index"] - 1
                    table_out[index][formatted_col] = found_comp_row[formatted_col]
                else:
                    row[formatted_col] = "error"
                    # FIND OUT WHAT CAN I DO HERE. THE OTHER VERSION COULD USE OLDER CODE FOR THIS PART

        # fifth run: format comps that have same value and autofit (and formatted value) in the same comp of other molecules (autofit not necessary)
        comp_groups = table_out.group_by("C")
        for comp_group in comp_groups.groups:
            comp = comp_group["C"][0]
            # skip groups with one row
            if len(comp_group) == 1:
                continue
            # skip if there are no autofitted and formatted values in group
            formatted_filter = comp_group[formatted_col] != '--'
            unformatted_filter = comp_group[formatted_col] == '--'
            if len(comp_group[formatted_filter]) == 0:
                continue
            for row in comp_group[unformatted_filter]:
                formula = row['Formula']
                found_value_filter = np.isclose(comp_group[value_col], row[value_col])
                if len(comp_group[formatted_filter & found_value_filter]) == 0:
                    continue
                elif len(comp_group[formatted_filter & found_value_filter]) == 1:
                    found_comp_row = comp_group[formatted_filter & found_value_filter][0]
                    # Now there is no need to get the significant values. THis is straight copy paste like I did in MADCUBA
                    index = row["Order_index"] - 1
                    table_out[index][formatted_col] = found_comp_row[formatted_col]
                else:
                    row[formatted_col] = "error"
                    # FIND OUT WHAT CAN I DO HERE. THE OTHER VERSION COULD USE OLDER CODE FOR THIS PART

        # sixth run: remaining values with no relation to other rows
        unformatted_filter = table_out[formatted_col] == '--'
        for row in table_out[unformatted_filter]:
            formula = row['Formula']
            comp = row['C']
            value = row[value_col]
            dummy, value_formatted, round_num = _return_significant_value(value)
            index = row["Order_index"] - 1
            table_out[index][formatted_col] = f"{value_formatted}"

    return table_out


def output_latex_molecular_parameters_table(table, fileout, mol_list='all'):
    """Output a Molecular Parameters Table as a filetext with code for a
    LaTeX table.

    Parameters
    ----------
    table : `~astropy.table.Table`
        Molecular Parameters Table.
    fileout : `str` or `pathlib.Path`
        Output file with the LaTeX table code.
    mol_list : `list`, optional
        List of molecule formulas to select for the LaTeX table.

    """

    # Format table columns if not pre-formatted
    if "formatted Width" not in table.colnames:
        fmt_table = format_molecular_parameters_columns(table)
    else:
        fmt_table = table

    # Select every molecule for 'all'
    if mol_list == 'all':
        mol_list = list(dict.fromkeys(fmt_table['Formula']))
    
    space_between_molecules = "    \\noalign{\\vskip 4pt}\n"

    # Write ascii file with the latex table text.
    with open(fileout, 'w') as f:
        # f.write('Molecule & N & Tex & v & width \n')
        # Loop through molecule formulas
        for i, formula in enumerate(mol_list):
            if i != 0:
                f.write(space_between_molecules)
            formula_table = fmt_table[fmt_table["Formula"] == formula]
            nrows = len(formula_table)
            previous_row_name_len = 0
            for j, row in enumerate(formula_table):
                # comp = row['C']
                # autofit = row['Autofit']
                # upper_limits_N = row['UpperLimits']
                # upper_limits_Tex = row['UpperLimitsTex']
                current_name = row['Label']
                if nrows > 1:
                    if j == 0:
                        label = f"\\multirow{{{nrows}}}{{*}}{{{current_name}}}"
                        previous_row_name_len = len(label)
                        name = label
                    else:
                        name = ' ' * previous_row_name_len
                else:
                    name = current_name
                
                # In each row write the following information sequentially
                f.write(f'    {name} &')
                # Column density
                formatted_N = row['formatted N/EM']
                if '<' in formatted_N:
                    formatted_N_latex = formatted_N.replace("<", "$<$")
                    f.write(f' {formatted_N_latex} &')
                elif'+/-' in formatted_N:
                    formatted_N_latex = formatted_N.replace(" +/- ", "$\\pm$")
                    f.write(f' {formatted_N_latex} &')
                else:
                    f.write(f' {formatted_N} &')
                # Tex
                formatted_Tex = row['formatted Tex/Te']
                if'+/-' in formatted_Tex:
                    formatted_Tex_latex = formatted_Tex.replace(" +/- ", "$\\pm$")
                    f.write(f' {formatted_Tex_latex} &')
                else:
                    f.write(f' {formatted_Tex} &')
                # Velocity
                formatted_vel = row['formatted Velocity']
                if'+/-' in formatted_vel:
                    formatted_vel_latex = formatted_vel.replace(" +/- ", "$\\pm$")
                    f.write(f' {formatted_vel_latex} &')
                else:
                    f.write(f' {formatted_vel} &')
                # Width
                formatted_width = row['formatted Width']
                if'+/-' in formatted_width:
                    formatted_width_latex = formatted_width.replace(" +/- ", "$\\pm$")
                    f.write(f' {formatted_width_latex} \\\\')
                else:
                    f.write(f' {formatted_width} \\\\')
                # Jump to the next line
                f.write('\n')
