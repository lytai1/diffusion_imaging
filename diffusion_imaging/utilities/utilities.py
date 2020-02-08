def load_affine(path_to_file, resulting_type):

    def _split_lines(matrix):
        
        out = []
        for line in matrix:
            out.append([val.rstrip() for val in line.split()])
            
        return out

    def _converter(val, resulting_type):
        
        return resulting_type(val)
                

    def _convert_type(matrix, converter, resulting_type):
        
        out = []
        for line in matrix:
            out.append([converter(val, resulting_type) for val in line])
            
        return out
        
    def _convert_affine_string(matrix, resulting_type):
        
        splitted_lines = _split_lines(matrix)
        resulting_matrix = _convert_type(splitted_lines, _converter, resulting_type)
        
        return resulting_matrix
    
    affine_matrix = []
    
    with open(path_to_file, "r") as f:
        affine_matrix = f.readlines()
        
    resulting_matrix = _convert_affine_string(affine_matrix, resulting_type)
            
    return resulting_matrix
