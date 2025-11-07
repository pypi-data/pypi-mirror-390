from adsdatahub.restapi.schemas._model import Model


def write_response_json(response: Model):
    with open("response.json", "w") as f:
        f.write(response.model_dump_json(indent=2, exclude_unset=True, by_alias=True))
