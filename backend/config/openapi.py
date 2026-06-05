"""Shared drf-spectacular helpers for consistent API documentation."""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

TAG_INVENTORY = 'Inventory'
TAG_INVOICES = 'Invoices'
TAG_REPORTS = 'Reports'
TAG_USERS = 'Users'

# Swagger UI parameter order (path params always first).
_PARAMETER_ORDER = (
    'start_date',
    'end_date',
    'search',
    'min_price',
    'max_price',
    'min_stock',
    'max_stock',
    'total_amount_min',
    'total_amount_max',
    'ordering',
    'page',
    'page_size',
    'cursor',
)
_PARAMETER_ORDER_INDEX = {name: index for index, name in enumerate(_PARAMETER_ORDER)}


def operation_parameter_sort_key(param: dict) -> tuple:
    """Keep related query parameters grouped in Swagger UI."""
    if param.get('in') == 'path':
        return (-1, param['name'])
    order = _PARAMETER_ORDER_INDEX.get(param['name'])
    if order is not None:
        return (order, '')
    return (len(_PARAMETER_ORDER), param['name'])


def search_param(*fields: str) -> OpenApiParameter:
    return OpenApiParameter(
        name='search',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        description=(
            'Case-insensitive search term. Matches any of: '
            + ', '.join(f'`{field}`' for field in fields)
            + '.'
        ),
    )


def ordering_param(*fields: str, default: str | None = None) -> OpenApiParameter:
    description = (
        'Sort results by a field. Prefix with `-` for descending order. '
        f'Allowed fields: {", ".join(fields)}.'
    )
    if default:
        description += f' Default: `{default}`.'
    return OpenApiParameter(
        name='ordering',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        description=description,
    )


def page_number_params() -> list[OpenApiParameter]:
    return [
        OpenApiParameter(
            name='page',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Page number for paginated results (1-based). Default: 1.',
        ),
        OpenApiParameter(
            name='page_size',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Number of results per page. Default: 20. Maximum: 100.',
        ),
    ]


def cursor_param() -> OpenApiParameter:
    return OpenApiParameter(
        name='cursor',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        required=False,
        description=(
            'Opaque cursor token from a previous response `next` or `previous` link. '
            'Omit on the first request.'
        ),
    )


def date_range_params(
    *,
    required: bool = False,
    max_days: int | None = None,
) -> list[OpenApiParameter]:
    range_note = (
        f' When both are provided, `start_date` must be on or before `end_date`.'
    )
    if max_days is not None:
        range_note += f' The range cannot exceed {max_days} days.'

    return [
        OpenApiParameter(
            name='start_date',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=required,
            description=(
                'Inclusive start of the date range (ISO 8601, e.g. `2025-01-01`).'
                + (' Required.' if required else ' Optional.')
                + range_note
            ),
        ),
        OpenApiParameter(
            name='end_date',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=required,
            description=(
                'Inclusive end of the date range (ISO 8601, e.g. `2025-01-31`).'
                + (' Required.' if required else ' Optional.')
            ),
        ),
    ]


def product_filter_params() -> list[OpenApiParameter]:
    return [
        OpenApiParameter(
            name='min_price',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Return products with `price` greater than or equal to this value (≥ 0).',
        ),
        OpenApiParameter(
            name='max_price',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Return products with `price` less than or equal to this value (≥ 0).',
        ),
        OpenApiParameter(
            name='min_stock',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Return products with `stock` greater than or equal to this value (≥ 0).',
        ),
        OpenApiParameter(
            name='max_stock',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Return products with `stock` less than or equal to this value (≥ 0).',
        ),
    ]


def invoice_filter_params() -> list[OpenApiParameter]:
    return [
        OpenApiParameter(
            name='total_amount_min',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Return invoices with `total_amount` greater than or equal to this value (≥ 0).',
        ),
        OpenApiParameter(
            name='total_amount_max',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Return invoices with `total_amount` less than or equal to this value (≥ 0).',
        ),
    ]


def path_id_param(resource: str) -> OpenApiParameter:
    return OpenApiParameter(
        name='id',
        type=OpenApiTypes.INT,
        location=OpenApiParameter.PATH,
        description=f'Primary key of the {resource}.',
    )
