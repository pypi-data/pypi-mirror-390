import numpy as np
import pandas as pd
import dask.array as da

class Expression:
    @classmethod
    def decorator(cls, function_call):
        def wrapper(*args, **kwargs):
            base = args[0]
            variables = args[1]  # variable(s) should always be first required argument
            if isinstance(variables, str):
                variables = [variables]

            post_process = kwargs.pop("post_process", None)

            # Handle magic vector variables.
            # Attempt to detect anything that ISN'T in the virtual variables set,
            # and thus set variables and post process appropriately.
            # Should work for anything ending in _x and _y
            extract_variables = []
            varmap = {}
            for var in variables:
                # We check now to see if the variable is listed in the "real" vars
                if var not in base.variables:
                    if "Dir" in var:
                        vars = base.vector_variables[var.replace("Dir", "")]

                        # arctan2 -> _y then _x.
                        pp = lambda x: (90 - np.arctan2(x[1], x[0]) * 180 / np.pi) % 360

                        extract_variables.extend(vars)
                        varmap[var] = (vars, pp)
                    else:
                        try:
                            vars = base.vector_variables[var]
                            pp = lambda x: np.hypot(*x)

                            extract_variables.extend(vars)
                            varmap[var] = (vars, pp)
                        except:
                            raise ValueError(
                                f"Variable(s) '{variables}' not found in dataset"
                            )

                elif var in base.variables:
                    extract_variables.append(var)
                    varmap[var] = (var, None)

            # Now we cut down to extracting only unique
            extract_variables = np.unique(extract_variables).tolist()

            data = {}
            for v in extract_variables:
                arr = function_call(base, v, *args[2:], **kwargs)
                data[v] = arr

            output = []
            for v, (vars, pp) in varmap.items():
                if pp is not None:
                    output.append(pp([data[x] for x in vars]))
                else:
                    output.append(data[v])
                    
            # Check if this is a dask array or not. 
            if isinstance(output[0], da.Array):
                output = da.stack(output)
            else:
                output = np.ma.stack(output)
            
            output = np.squeeze(output)

            if post_process:
                output = post_process(output.astype(float))

            return output

        return wrapper


def unsupported_decorator(function_call):
    def wrapper(*args):
        name = function_call.__name__
        message = "{} is currently not supported".format(name)
        print(message)

    return wrapper
