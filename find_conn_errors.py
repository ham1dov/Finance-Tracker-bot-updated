import ast

def check_file(filename):
    with open(filename, 'r') as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef):
            has_conn_acquire = False
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.withitem):
                    if isinstance(subnode.context_expr, ast.Call):
                        if hasattr(subnode.context_expr.func, 'attr') and subnode.context_expr.func.attr == 'acquire':
                            if subnode.optional_vars and hasattr(subnode.optional_vars, 'id') and subnode.optional_vars.id == 'conn':
                                has_conn_acquire = True

                if isinstance(subnode, ast.Name) and subnode.id == 'conn':
                    # Check if it's being used (load)
                    if isinstance(subnode.ctx, ast.Load) and not has_conn_acquire:
                        # We need to be more precise, but this is a start
                        # A better check would be if the use is inside the 'with' block
                        pass

if __name__ == "__main__":
    # Simplified check: just find all await conn.xxx and see if there is a 'with ... as conn' above it in the same function
    with open('database/db_query.py', 'r') as f:
        lines = f.readlines()

    current_func = None
    has_with_conn = False
    for i, line in enumerate(lines):
        if 'async def ' in line:
            current_func = line.strip()
            has_with_conn = False
        if 'async with self.pool.acquire() as conn:' in line or 'async with self.pool.acquire() as connection:' in line:
            has_with_conn = True
        if 'await conn.' in line and not has_with_conn:
            print(f"Potential error in {current_func} at line {i+1}: {line.strip()}")
        if 'await connection.' in line and not has_with_conn:
            print(f"Potential error in {current_func} at line {i+1}: {line.strip()}")
