from typing import Union


def convert_generic_parameters_to_string(generic_parameter_dict: dict) -> str:
    output_str = ""
    for p, v in zip(
        generic_parameter_dict["data_dict"]["Parameter"],
        generic_parameter_dict["data_dict"]["Value"],
    ):
        output_str += p.replace("___", " ") + " " + str(v) + "\n"
    return output_str[:-1]


def convert_generic_parameters_to_dictionary(generic_parameter_dict: dict) -> dict:
    return {
        p: v
        for p, v in zip(
            generic_parameter_dict["data_dict"]["Parameter"],
            generic_parameter_dict["data_dict"]["Value"],
        )
    }


def convert_datacontainer_to_dictionary(data_container_dict: dict) -> dict:
    output_dict = _sort_dictionary_from_datacontainer(
        input_dict=_filter_dict(
            input_dict=data_container_dict,
            remove_keys_lst=[
                "NAME",
                "TYPE",
                "OBJECT",
                "DICT_VERSION",
                "HDF_VERSION",
                "READ_ONLY",
                "VERSION",
            ],
        )
    )
    if isinstance(output_dict, dict):
        return output_dict
    else:
        raise TypeError("datacontainer was not converted to a dictionary.")


def _filter_dict(input_dict: dict, remove_keys_lst: list) -> dict:
    def recursive_filter(input_value: dict, remove_keys_lst: list) -> dict:
        if isinstance(input_value, dict):
            return _filter_dict(input_dict=input_value, remove_keys_lst=remove_keys_lst)
        else:
            return input_value

    return {
        k: recursive_filter(input_value=v, remove_keys_lst=remove_keys_lst)
        for k, v in input_dict.items()
        if k not in remove_keys_lst
    }


def _sort_dictionary_from_datacontainer(input_dict: dict) -> Union[dict, list]:
    def recursive_sort(input_value: dict) -> Union[dict, list]:
        if isinstance(input_value, dict):
            return _sort_dictionary_from_datacontainer(input_dict=input_value)
        else:
            return input_value

    ind_dict, content_dict = {}, {}
    content_lst_flag = False
    for k, v in input_dict.items():
        if "__index_" in k:
            key, ind = k.split("__index_")
            if key == "":
                content_lst_flag = True
                ind_dict[int(ind)] = recursive_sort(input_value=v)
            else:
                ind_dict[int(ind)] = key
                content_dict[key] = recursive_sort(input_value=v)
        else:
            content_dict[k] = recursive_sort(input_value=v)
    if content_lst_flag:
        return [ind_dict[ind] for ind in sorted(list(ind_dict.keys()))]
    elif len(ind_dict) == len(content_dict):
        return {
            ind_dict[ind]: content_dict[ind_dict[ind]]
            for ind in sorted(list(ind_dict.keys()))
        }
    elif len(ind_dict) == 0:
        return content_dict
    else:
        raise KeyError(ind_dict, content_dict)
