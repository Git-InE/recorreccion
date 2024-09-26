import re

'''
    ***
    Parametro 1 : nombre : str
    Parametro 2 : tipo : str, opcional
    Parametro 3 : valor : cualquier tipo, opcional
    ***
    None
    ***
    Inicializa una nueva variable con nombre, tipo, y valor opcionales.
    '''
class Variable:
    def __init__(self, nombre, tipo=None, valor=None):
        self.nombre = nombre
        self.tipo = tipo
        self.valor = valor
    '''
    ***
    Parametro 1 : valor : cualquier tipo
    ***
    None
    ***
    Asigna un valor a la variable, determinando su tipo. Lanza una excepción si el tipo no es soportado.
    '''
    def asignar_valor(self, valor):
        if isinstance(valor, int):
            self.tipo = 'int'
        elif isinstance(valor, bool):
            self.tipo = 'bool'
        elif valor.startswith('#') and valor.endswith('#'):
            self.tipo = 'string'
        else:
            raise ValueError(f"Tipo de dato no soportado para la variable {self.nombre}")
        self.valor = valor
    '''
    ***
    Ningún parámetro
    ***
    str
    ***
    Retorna una representación en cadena de la variable, mostrando su nombre, tipo, y valor.
    '''
    def __str__(self):
        return f"{self.nombre} ({self.tipo}): {self.valor}"

variables = {}
# Patrones generales
patrones_globales = [
    ('DEFINE', r'^DEFINE\s+\$_[A-Z]+\w*\d*$'),                                                                          # Ej: DEFINE $_Var
    ('DP_ASIG', r'^\s*DP\s+\$_[A-Z]+\w*\s+ASIG\s+(?P<valor>.*)$'),                                                      # DP $_Var1 ASIG ...
    ('DP_SUMA', r'^DP\s+\$_[A-Z]+\w*\s+\+\s+\$_[A-Z]+\w*\s+(([1-9][0-9]*\s*)|\$_[A-Z]+\w*)$'),                          # DP $_Var1 + ...
    ('DP_MULTI', r'^DP\s+\$_[A-Z]+\w*\s+\*\s+\$_[A-Z]+\w*\s+(([1-9][0-9]*\s*)|\$_[A-Z]+\w*)$'),                         # DP $_Var1 * ...
    ('DP_GT', r'^DP\s+\$_[A-Z]+\w*\s+>\s+\$_[A-Z]+\w*\s+(([1-9][0-9]*\s*)|\$_[A-Z]+\w*)$'),                             # DP $_Var1 > ...
    ('DP_EQ', r'^DP\s+\$_[A-Z]+\w*\s+==\s+\$_[A-Z]+\w*\s+(([1-9][0-9]*\s*)|\$_[A-Z]+\w*)$'),                            # DP $_Var1 == ...
    ('MOSTRAR', r'^MOSTRAR\s*\(\$_[A-Z]+\w*\)'),                                                                           # Ej: MOSTRAR($_Var)
    ('CONDICIONAL', r'^if\s*\((?P<condicion>[^)]+)\)\s*\{(?P<codigo_if>.*?)\}(?:\s*else\s*\{(?P<codigo_else>.*?)\})?$'),  # if-else completo
    ('IF', r'^if\s*\([^)]+\)\s*\{'),
    ('ELSE', r'\}\s*else\s*\{'),
    ('FIN_IF', r'\}\s*$'),
]

# Patrones internos para desglosar elementos
patrones_internos = [
    ('VARIABLE', r'\$_[A-Z]+\w*'),                       # Variables
    ('ASIG', r'\bASIG\b'),                               # Operador de asignación
    ('VALOR', r'\#[^#]*\#|\b[1-9][0-9]*\b|True|False'),      # Valores (números, booleanos, strings)
    ('OPERADOR', r'\+|\*|>|=='),                         # Operadores binarios
]
patrones_condicionales = [
    ('IF', r'^if\s*\([^)]+\)\s*\{'),
    ('ELSE', r'\}\s*else\s*\{')
]
'''
***
Parametro 1 : linea_simple : str
***
tupla
***
Identifica y retorna el nombre del comando y la línea si coincide con algún patrón global. Lanza una excepción en caso de error de sintaxis.
'''
def identificar_comando(linea_simple):
    for nombre, patron in patrones_globales:
        if re.match(patron, linea_simple):
            return nombre, linea_simple
    raise SyntaxError(f'Mal Sintaxis: La línea "{linea_simple}" no está bien escrita.')

'''
***
Parametro 1 : linea_simple : str
***
lista
***
Separa una línea simple en tokens internos según los patrones internos. Retorna una lista de tokens.
'''
def separar_linea(linea_simple):
    tokens_internos = []
    for nombre_interno, patron_interno in patrones_internos:
        for match in re.finditer(patron_interno, linea_simple):
            tokens_internos.append((nombre_interno, match.group()))
    return tokens_internos

'''
***
Parametro 1 : linea_simple : str
***
bool
***
Verifica si la asignación en la línea es válida, asegurando que no hay múltiples valores. Retorna True si es válida; lanza una excepción en caso contrario.
'''
def verificar_asignacion(linea_simple):
    match = re.match(patrones_globales[1][1], linea_simple)
    if match:
        valor = match.group('valor').strip()
        # Detectar y extraer las cadenas entre `#`
        valores = re.findall(r'#.*?#|[^\s#]+', valor)
        
        if len(valores) > 1:
            raise ValueError(f"Error: Se están asignando múltiples valores en la línea: {linea_simple}")
        
        if re.match(patrones_internos[2][1], valores[0]):
            return True
        
        else:
            raise ValueError(f"Error: Valor inválido en la línea: {linea_simple}")
    else:
        raise SyntaxError(f"Error de sintaxis en la línea: {linea_simple}")
    return
'''
***
Parametro 1 : nombre : str
Parametro 2 : tokens_internos : list
Parametro 3 : linea_simple : str
***
None
***
Ejecuta el comando identificado, aplicando la lógica correspondiente según el nombre del comando.
Lanza excepciones en caso de errores o valores no válidos.
'''
def ejecutar_comando(nombre, tokens_internos, linea_simple):
    if nombre == 'DEFINE':
        var_name = tokens_internos[0][1]
        if var_name in variables:
            raise ValueError(f"Variable Ya Definida: La variable {var_name} ya se encuentra definida.")
        variables[var_name] = Variable(nombre=var_name)
    elif nombre == 'DP_ASIG':
        verificar_asignacion(linea_simple)  # Aseguramos que la línea actual se pasa a la verificación
        var_dest = tokens_internos[0][1]
        valor = tokens_internos[2][1]
        
        if var_dest not in variables:
            raise ValueError(f"Variable No Definida: La variable {var_dest} no ha sido definida.")
        
        if re.match(r'\#[^#]*\#', valor):
            variables[var_dest].asignar_valor(valor)
        
        elif re.match(r'\s*0\s*|\s*[1-9][0-9]*', valor):
            variables[var_dest].asignar_valor(int(valor))
        
        elif re.match(r'\bTrue\b|\bFalse\b', valor):
            variables[var_dest].asignar_valor(bool(valor))
        
        else:
            raise ValueError(f"Tipo de dato ({valor}) no soportado")

    elif nombre == 'DP_SUMA':
        var_dest = tokens_internos[0][1]
        var1 = tokens_internos[1][1]
        var2 = tokens_internos[2][1]
    
        if var_dest not in variables or var1 not in variables or var2 not in variables:
            raise ValueError(f"Variable No Definida: Una de las variables no ha sido definida.")
        variables[var_dest].valor = variables[var1].valor
    
        if var2.startswith('#') and var2.endswith('#'): 
            valor2 = var2
        elif isinstance(variables[var_dest].valor, bool) or isinstance(variables[var2].valor, bool):
            raise ValueError(f"Operación no permitida: No se permite la suma de booleanos")
        elif var2.isdigit(): 
            valor2 = int(var2)
        else: 
            if var2 not in variables:
                raise ValueError(f"Variable No Definida: {var2}")
            valor2 = variables[var2].valor
    
        if isinstance(variables[var_dest].valor, str) or isinstance(valor2, str):
            variables[var_dest].valor += str(valor2)
        else:
            variables[var_dest].valor += valor2
    
    elif nombre == 'DP_MULTI':
        var_dest = tokens_internos[0][1]
        var1 = tokens_internos[1][1]
        var2 = tokens_internos[2][1]

        if var_dest not in variables or var1 not in variables or var2 not in variables:
            raise ValueError(f"Variable No Definida: Una de las variables no ha sido definida.")
        variables[var_dest].valor = variables[var1].valor
        
        if isinstance(variables[var_dest].valor, bool) or isinstance(variables[var2].valor, bool):
            raise ValueError(f"Operación no permitida: No se puede multiplicar un valor booleano")
        
        if var2.startswith('#') and var2.endswith('#'): 
            raise ValueError(f"Operación no permitida: No se puede multiplicar un string por un valor")
        
        elif var2.isdigit(): 
            valor2 = int(var2)
        
        else: 
            if var2 not in variables:
                raise ValueError(f"Variable No Definida: {var2}")
            valor2 = variables[var2].valor

        variables[var_dest].valor *= valor2

    elif nombre == 'DP_GT':
        var_dest = tokens_internos[0][1]
        var1 = tokens_internos[1][1]
        var2 = tokens_internos[2][1]

        if var_dest not in variables or var1 not in variables or var2 not in variables:
            raise ValueError(f"Variable No Definida: Una de las variables no ha sido definida.")

        # Asignar el valor de var1 a var_dest
        variables[var_dest].valor = variables[var1].valor

        # Comparar var2 con var_dest
        if var2.startswith('#') and var2.endswith('#'): 
            raise ValueError(f"Operación no permitida: Solo se puede comparar valores de tipo entero.")
        
        elif isinstance(variables[var_dest].valor, bool) or isinstance(variables[var2].valor, bool):
            raise ValueError(f"Operación no permitida: Solo se puede comparar valores de tipo entero.")
        
        elif var2.isdigit(): 
            valor2 = int(var2)
        
        else: 
            if var2 not in variables:
                raise ValueError(f"Variable No Definida: {var2}")
            valor2 = variables[var2].valor

        if not isinstance(variables[var_dest].valor, int) or not isinstance(valor2, int):
            raise ValueError(f"Operación no permitida: No se puede comparar un valor no entero")

        variables[var_dest].valor = variables[var_dest].valor > valor2

    elif nombre == 'DP_EQ':
        var_dest = tokens_internos[0][1]
        var1 = tokens_internos[1][1]
        var2 = tokens_internos[2][1]

        if var_dest not in variables or var1 not in variables or var2 not in variables:
            raise ValueError(f"Variable No Definida: Una de las variables no ha sido definida.")
        # Asignar el valor de var1 a var_dest
        variables[var_dest].valor = variables[var1].valor
        if isinstance(variables[var_dest].valor, bool) or isinstance(variables[var2].valor, bool):
            raise ValueError(f"Operación no permitida: No se puede comparar valores de tipo booleano")
        # Comparar var2 con var_dest
        if var2.startswith('#') and var2.endswith('#'):  # string value
            valor2 = var2
        elif var2.isdigit():  # integer value
            valor2 = int(var2)
        else:  # assume it's a variable
            if var2 not in variables:
                raise ValueError(f"Variable No Definida: {var2}")
            valor2 = variables[var2].valor

        if isinstance(variables[var_dest].valor, str) and isinstance(valor2, str):
            variables[var_dest].valor = variables[var_dest].valor == valor2
        elif isinstance(variables[var_dest].valor, int) and isinstance(valor2, int):
            variables[var_dest].valor = variables[var_dest].valor == valor2
        else:
            raise ValueError(f"Operación no permitida: No se puede comparar valores de tipos diferentes")

    elif nombre == 'MOSTRAR':
        var_name = tokens_internos[0][1]
        if var_name not in variables:
            raise ValueError(f"Variable No Definida: La variable {var_name} no ha sido definida.")
        valor = str(variables[var_name].valor)
        # Eliminar los caracteres # del string
        valor = re.sub(r'#', '', valor)
        with open('output.txt', 'a') as output:
            output.write(str(valor) + '\n')
        
    elif nombre == 'IF' or 'ELSE' or 'FIN_IF':
        return
    elif nombre == 'CONDICIONAL':
        match = re.match(patrones_globales[7][1], linea_simple)
        if match:
            condicion = match.group('condicion')
            codigo_if = match.group('codigo_if').strip().splitlines()
            codigo_else = match.group('codigo_else').strip().splitlines() if match.group('codigo_else') else []
            if evaluar_condicion_if(condicion):
                ejecutar_codigo(codigo_if)
            elif codigo_else:
                ejecutar_codigo(codigo_else)
        else:
            raise SyntaxError(f"Error de sintaxis en la línea: {linea_simple}")
    return

'''
***
Parametro 1 : condicion : str
***
bool
***
Evalúa la condición de un bloque if para decidir si debe ejecutarse o no el código dentro de él. Retorna True si la condición es verdadera, False en caso contrario.
'''
def evaluar_condicion_if(condicion):
    # Evalúa la condición de un if
    tokens = separar_linea(condicion)
    var_name = tokens[0][1]
    return variables[var_name].valor

'''
    ***
    Parametro 1 : List[str]
    ***
    None
    ***
    Recorre el bloque de líneas de código, evaluando y ejecutando comandos
    y estructuras condicionales según sea necesario.
    '''
def ejecutar_codigo(bloque_de_lineas):
    i = 0
    while i < len(bloque_de_lineas):
        linea_simple = bloque_de_lineas[i].strip()
        if re.match(patrones_condicionales[0][1], linea_simple): #verificar estructura if
            match = re.match(patrones_globales[7][1], linea_simple)
            if match:
                condicion = match.group('condicion')
                codigo_if = match.group('codigo_if').strip().splitlines()
                codigo_else = match.group('codigo_else').strip().splitlines() if match.group('codigo_else') else []
                
                if evaluar_condicion_if(condicion): #ejecuta segun if o else
                    ejecutar_codigo(codigo_if)
                elif codigo_else:
                    ejecutar_codigo(codigo_else)
            else:
                raise SyntaxError(f"Error de sintaxis en la línea: {linea_simple}")
        else: #ejecuta comandos simples
            nombre, linea_simple = identificar_comando(linea_simple)
            tokens_internos = separar_linea(linea_simple)
            ejecutar_comando(nombre, tokens_internos, linea_simple)
        i += 1
    return

    '''
    ***
    Parametro 1 : List[List[str]]
    Parametro 2 : List[str]
    ***
    None
    ***
    Inserta un bloque de código en la pila si no está vacío el bloque.
    '''
def insertar_bloque(stack, bloque):
    if bloque:
        stack.append(bloque)
    return

'''
***
None
***
None
***
Lee el archivo de código, procesa las líneas para identificar y ejecutar
bloques de código condicionales y simples, manejando errores de sintaxis y
valor.
PD: Disculpar lo denso que resulta esta función, era la unica manera de asegurarme que no existieran errores
    por los bloques if-else y su compleja implementación. Lo compensare comentando parte por parte.
'''
def main():
    with open('codigo.txt', 'r') as archivo:
        lines = archivo.readlines()
        linea_actual = 0
        profundidad = 1
        while linea_actual < len(lines):
            try:
                line = lines[linea_actual].strip()
                # Solo se ejecuta si hace match con el patron de un if ("if ($_Var1..) {" )
                if re.match(patrones_condicionales[0][1], line): #if
                    stack = []
                    corchetes = [] #para posterior verificacion de los bloques del if y else
                    condicion = evaluar_condicion_if(line) #condicion True o False
                    if condicion:  #bloque if
                        bloque_if = []
                          
                        if "{" in line:
                            corchetes.append("{")
                        if "}" in line:
                            corchetes.pop()
                            
                        while linea_actual + 1 < len(lines):
                            linea_actual += 1
                            line = lines[linea_actual].strip()
                            
                            if re.match(patrones_condicionales[0][1], line): #En caso de que exista un if anidado
                                insertar_bloque(stack, bloque_if)
                                bloque_if = []
                                profundidad += 1
                                
                            elif re.match(patrones_condicionales[1][1], line): #Caso donde se cierra un bloque if
                                insertar_bloque(stack, bloque_if)
                                bloque_if = []
                                profundidad -=1
                                
                                if profundidad == 0: # Nivel 0 de indentacion
                                    insertar_bloque(stack, bloque_if)
                                    bloque_if = []
                                    break
                                
                                elif profundidad == -1:
                                    raise Exception(f"Error inesperado en la línea {linea_actual + 1}: Profundidad negativa")
                            
                            if len(stack) > 3:
                                raise SyntaxError("Máximo 3 bloques de if-else anidados")
                            bloque_if.append(line)
                        # Ejecucion con metodo Stack    
                        while len(stack) > 0:
                            ejecutar_codigo(stack[-1])
                            stack.pop()
                        stack.clear()
                        # Verificacion que el bloque if-else correspondiente no se siga leyendo nuevamente luego de la ejecucion
                        while len(corchetes) != 0:
                            line = lines[linea_actual].strip()
                            if "{" in line:
                                corchetes.append("{")
                            if "}" in line:
                                corchetes.pop()
                            linea_actual += 1
                        
                    else: # Caso False
                        while not re.match(patrones_condicionales[1][1], line):
                            linea_actual += 1
                            line = lines[linea_actual].strip()
                        bloque_else = []
                        
                        while linea_actual + 1 < len(lines):
                            linea_actual += 1
                            line = lines[linea_actual].strip()
                            
                            if re.match(patrones_condicionales[0][1], line): # Caso de encontrar un if dentro del else
                                insertar_bloque(stack, bloque_else)
                                condicion = evaluar_condicion_if(line)
                                
                                if not condicion: # si el if resultante contiene un valor False (ver linea 480)
                                    break
                                
                                linea_actual += 1
                                line = lines[linea_actual].strip()
                                bloque_else = []
                                profundidad += 1
                                break
                            
                            elif re.match(patrones_condicionales[1][1], line) or re.match(r'\s*\}\s*\n*', line): #else o "}"
                                profundidad -=1
                                
                                if profundidad == 0:
                                    insertar_bloque(stack, bloque_else)
                                    bloque_else = []
                                    break
                                
                                elif profundidad == -1:
                                    raise Exception(f"Error inesperado en la línea {linea_actual + 1}: Profundidad negativa")
                            
                            if len(stack) > 3:
                                raise SyntaxError("Máximo 3 bloques de if-else anidados")
                            bloque_else.append(line)
                            
                        while len(stack) > 0:
                            ejecutar_codigo(stack[-1])
                            stack.pop()
                        stack.clear()
                        
                        if not condicion: # Se salta un ciclo
                            continue
                
                if re.match(r'\s*\}\s*\n*', line) and linea_actual + 1 < len(lines): # Caso linea solo con "}"
                    linea_actual += 1
                    line = lines[linea_actual].strip()
                    continue
                
                else:
                    # Manejar líneas simples
                    nombre, linea_simple = identificar_comando(line)
                    tokens_internos = separar_linea(linea_simple)
                    ejecutar_comando(nombre, tokens_internos, linea_simple)
            # Puede que existan problemas en la lectura del numero de linea en caso de if-else anidados, por la forma en la que
            # se manejan estos bloques (Stack), pero la linea del mensaje debe estar correcta,
            # es decir, el indice indicara el final del bloque pero la linea donde ocurre el error debe ser la correcta.
            except SyntaxError as err:
                raise SyntaxError(f"Error de sintaxis en la línea {linea_actual + 1}: {err}")
            
            except ValueError as err:
                raise ValueError(f"Error de valor en la línea {linea_actual + 1}: {err}")
            
            except Exception as err:
                raise Exception(f"Error inesperado en la línea {linea_actual + 1}: {err}")
            linea_actual += 1
            
    archivo.close()
    return 0    
   
if __name__ == "__main__":
    main()