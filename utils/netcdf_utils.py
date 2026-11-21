import netCDF4
import numpy as np


def open_netcdf(file_path):
    """Open a NetCDF dataset."""
    return netCDF4.Dataset(file_path, mode="r")


def close_netcdf(dataset):
    """Close an opened NetCDF dataset."""
    if dataset is not None:
        dataset.close()


def get_global_attributes(dataset):
    """Return global attributes of the dataset."""
    return {
        attr: dataset.getncattr(attr)
        for attr in dataset.ncattrs()
    }


def get_dimensions(dataset):
    """Return dimensions of the root dataset."""
    return {
        name: len(dimension)
        for name, dimension in dataset.dimensions.items()
    }


def get_group_names(dataset):
    """Return group names recursively."""
    group_names = []

    def explore(group, prefix=""):
        for name, subgroup in group.groups.items():
            full_name = f"{prefix}/{name}" if prefix else f"/{name}"
            group_names.append(full_name)
            explore(subgroup, full_name)

    explore(dataset)
    return group_names


def get_variable_catalog(dataset):
    """Return catalog of variables from all groups."""

    catalog = []

    def explore(group, group_path="/"):
        for name, variable in group.variables.items():

            catalog.append({
                "group": group_path,
                "variable": name,
                "shape": variable.shape,
                "dtype": str(variable.dtype),
                "dimensions": variable.dimensions,
                "attributes": {
                    attr: variable.getncattr(attr)
                    for attr in variable.ncattrs()
                }
            })

        for name, subgroup in group.groups.items():
            new_path = (
                f"{group_path.rstrip('/')}/{name}"
                if group_path != "/"
                else f"/{name}"
            )
            explore(subgroup, new_path)

    explore(dataset)

    return catalog


def get_variable(dataset, variable_name, group_path="/"):
    """Retrieve a variable from a specific group."""

    group = dataset

    if group_path and group_path != "/":
        for group_name in group_path.strip("/").split("/"):
            group = group.groups[group_name]

    return group.variables[variable_name]


def get_variable_sample(variable, sample_size=10):
    """Extract a small sample of variable data."""

    if variable.ndim == 0:
        return variable[()]

    slices = tuple(
        slice(0, min(sample_size, size))
        for size in variable.shape
    )

    return variable[slices]


def get_variable_value(variable, indices=None):
    """Extract a specific value or data slice."""

    if indices is None:
        if variable.ndim == 0:
            return variable[()]

        return variable[:]

    return variable[indices]
