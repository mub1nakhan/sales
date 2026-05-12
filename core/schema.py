from drf_spectacular.utils import extend_schema_view, extend_schema

_CRUD = ["list", "create", "retrieve", "update", "partial_update", "destroy"]


def schema_view(*tags, **summaries):
    """
    ViewSet standart amallariga tag va summary qo'shuvchi decorator.

    Foydalanish:
        @schema_view("Products", list="Ro'yxat", create="Yaratish")
        class ProductViewSet(viewsets.ModelViewSet): ...
    """
    kwargs = {
        act: extend_schema(tags=list(tags), summary=summaries.get(act))
        for act in _CRUD
    }
    return extend_schema_view(**kwargs)
