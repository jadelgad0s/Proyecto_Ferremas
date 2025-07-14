from rest_framework import serializers
from .models import Producto, Proveedor, TipoProducto

class ProductoSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()
    id_proveedor = serializers.PrimaryKeyRelatedField(queryset=Proveedor.objects.all())
    id_tipo_producto = serializers.PrimaryKeyRelatedField(queryset=TipoProducto.objects.all())

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'precio', 'stock', 'imagen_url', 'imagen', 'id_proveedor', 'id_tipo_producto']

    def get_imagen_url(self, obj):
        request = self.context.get('request')
        if obj.imagen and request:
            return request.build_absolute_uri(obj.imagen.url)
        elif obj.imagen:
            return obj.imagen.url
        return None
