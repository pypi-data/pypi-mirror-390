import re


class CosmosDBForNoSQLValidators:
    @staticmethod
    def validate_property_paths(paths: list):
        for path in paths:
            res = True
            if not path.startswith('/') or path.endswith('/*'):
                res = False
            else:
                segments = path.strip('/').split('/')

                for segment in segments:
                    if not segment:
                        continue
                    if not re.match(r'^[a-zA-Z0-9_.-]*$', segment):
                        res = False

            if not res:
                raise ValueError(f"Property path: {path} is not a valid path")
