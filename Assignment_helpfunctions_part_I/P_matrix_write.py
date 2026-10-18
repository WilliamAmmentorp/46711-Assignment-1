# -*- coding: utf-8 -*-
"""
Write participation matrix to LaTeX table or Excel

@author: chhil
"""

import xlwt
import numpy as np

def latex_P_matrix(P,state_labels,Matlab_array,filename,maximum_col,bold_limit):
    # P = Participation matrix
    # state_labels = labels of entries in the statevector
    # Matlab_array = True if the state_labels comes from a cell array in Matlab
    # filename = Name of the file to write the latex document in
        
    limit = bold_limit # Limit for making value bold
    n_elm = maximum_col # Number of elements pr. table
    n1 = (P.shape)[0] # Shape of P
    n2 = (P.shape)[1] # Shape of P
    N = int(np.ceil(n2/n_elm)) # Number of iteration
    n_hlines = 7 # Horizontal line pr. 6 values
    counter = 1 
    fid = open(filename,'w') # Open file with write access
    
    # Create a table pr. 4 eigenvalues
    for h in range(0,N):
        fid.write('\\begin{tabular}{')
        if h<N-1: # Number of elemest for all but last table            
            for k in range(0,n_elm):
                fid.write('l')
                if k == n_elm-1:
                    fid.write('|l}\r')
                
        
        else: # Last table should only be as wide as remaining eigenvalues            
            for k in range (0,n2-(N-1)*n_elm):
                    fid.write('l')
                    if k==n2-(N-1)*n_elm-1:
                        fid.write('|l}\r')
                   
        for k in range(0,n1):                    
            if h<N-1: # All but last has n_elm columns
                for l in range(h*n_elm,(h+1)*n_elm):
                    # Bold if abs larger than limit
                    if (np.abs(P[k,l])>=limit):
                        fid.write('$\\mathbf{(%.3f \\angle %.2f)}$\t& ' % (np.abs(P[k,l]),np.angle(P[k,l], deg=True)))                   
                    else:
                        fid.write('$(%.3f \\angle %.2f)$\t& ' % (np.abs(P[k,l]),np.angle(P[k,l], deg=True)))
                    
            else: # Last is only remaining values wide
                 for l in range(h*n_elm,n2):
                    # Bold if abs larger than limit
                    if (np.abs(P[k,l])>=limit):
                        fid.write('$\\mathbf{(%.3f \\angle %.2f)}$\t& ' % (np.abs(P[k,l]),np.angle(P[k,l], deg=True)))
                    else:
                        fid.write('$(%.3f \\angle %.2f)$\t& ' % (np.abs(P[k,l]),np.angle(P[k,l], deg=True)))
            # Labels for state vectors
            if (Matlab_array):
                fid.write('$%s$ \\\\ \r' % (state_labels[k,0][0]))
            else:
                fid.write('$%s$ \\\\ \r' % (state_labels[k]))
            
            # Horizontal line pr. n_hlines state variables
            if (k==n_hlines*counter-1 and k != n1-1):
                fid.write(' \\hline \r')                
                counter += 1
        # 2 horizontal lines at end        
        fid.write(' \\hline \r\\hline \r')
        
        # Put labels for eigenvalues below table
        if h<N-1:
            for l in range(1+h*n_elm,(h+1)*n_elm+1):
                fid.write('$\\qquad\\lambda_{%i}$\t&' % (l))   
            
        else:
             for l in range(1+h*n_elm,n2+1):
                 fid.write('$\\qquad\\lambda_{%i}$\t&' % (l))   
             
        # End table
        fid.write('\r\\end{tabular}\r\r')
        
        counter = 1
    
    # Close file
    fid.close()
    
    return


def excel_P_matrix(P, state_labels, Matlab_array, filename, bold_limit):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Border, Side

    limit = bold_limit
    bold_font = Font(bold=True)
    left_border = Border(left=Side(style='thin'))
    top_double_border = Border(top=Side(style='double'))

    wb = Workbook()
    ws = wb.active
    ws.title = 'Participation matrix'

    n1, n2 = P.shape

    for i in range(n1):
        for j in range(n2):
            cell = ws.cell(row=i+1, column=j+1, value=round(float(np.abs(P[i, j])), 3))
            if np.abs(P[i, j]) > limit:
                cell.font = bold_font

        label = state_labels[i, 0][0] if Matlab_array else state_labels[i]
        label_cell = ws.cell(row=i+1, column=n2+1, value=label)
        label_cell.border = left_border

    for j in range(n2):
        name = f"\N{GREEK SMALL LETTER LAMDA}_{j+1}"
        cell = ws.cell(row=n1+1, column=j+1, value=name)
        cell.border = top_double_border

    wb.save(filename)