import json
import anthropic

client = anthropic.Anthropic()

# 1. Función real que ejecutará el agente
def calcular_total(precio_unitario: float, cantidad: int, descuento_pct: float = 0.0) -> str:
    subtotal = precio_unitario * cantidad
    total = subtotal * (1 - descuento_pct / 100.0)
    return json.dumps({"subtotal": subtotal, "total": round(total, 2)})

# 2. Esquema de la herramienta para Claude
tools = [
    {
        "name": "calcular_total",
        "description": "Calcula el subtotal y el total con descuento opcional de una compra.",
        "input_schema": {
            "type": "object",
            "properties": {
                "precio_unitario": {"type": "number", "description": "Precio por unidad"},
                "cantidad": {"type": "integer", "description": "Cantidad de unidades"},
                "descuento_pct": {"type": "number", "description": "Descuento en porcentaje (0 a 100)"},
            },
            "required": ["precio_unitario", "cantidad"],
        },
    }
]

def ejecutar_agente(objetivo: str) -> str:
    mensajes = [{"role": "user", "content": objetivo}]

    while True:
        respuesta = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            system="Eres un agente útil. Usa las herramientas disponibles cuando necesites calcular valores.",
            tools=tools,
            messages=mensajes,
        )

        # Si Claude ya terminó sin pedir más herramientas, devolvemos su respuesta final
        if respuesta.stop_reason != "tool_use":
            textos = [bloque.text for bloque in respuesta.content if bloque.type == "text"]
            return "\n".join(textos)

        # Agregamos la respuesta del asistente (incluye los bloques tool_use)
        mensajes.append({"role": "assistant", "content": respuesta.content})

        # Ejecutamos cada herramienta solicitada y devolvemos los resultados
        resultados_herramientas = []
        for bloque in respuesta.content:
            if bloque.type == "tool_use" and bloque.name == "calcular_total":
                try:
                    args = bloque.input
                    salida = calcular_total(
                        precio_unitario=args["precio_unitario"],
                        cantidad=args["cantidad"],
                        descuento_pct=args.get("descuento_pct", 0.0),
                    )
                    resultados_herramientas.append({
                        "type": "tool_result",
                        "tool_use_id": bloque.id,
                        "content": salida,
                    })
                except Exception as e:
                    resultados_herramientas.append({
                        "type": "tool_result",
                        "tool_use_id": bloque.id,
                        "content": f"Error al ejecutar herramienta: {e}",
                        "is_error": True,
                    })

        mensajes.append({"role": "user", "content": resultados_herramientas})

if __name__ == "__main__":
    print(ejecutar_agente("Quiero 3 licencias a 49.50 cada una con 15% de descuento."))
