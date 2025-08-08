##Generacion de mapas=group
##Mapa de calor Reclamos=name
##Ingrese_tu_capa_vectorial=vector
##Tipo_de_base_map=selection Mapa_De_Calor;Agrupador
##Formato_de_salida=output html

library(leaflet)
library(leaflet.extras)
library(htmlwidgets)
library(sf)


# Crear geometría desde coordenadas RecX / RecY (EPSG:22192)
Layer <- st_as_sf(Ingrese_tu_capa_vectorial,
                  coords = c("RecX", "RecY"),
                  crs = 22192)

# Transformar a WGS84 (EPSG:4326)
Layer <- st_transform(Layer, 4326)

# Extraer coordenadas para Leaflet
coords <- st_coordinates(Layer)
Layer$longitude <- coords[, 1]
Layer$latitude <- coords[, 2]

# Selección del mapa base
if (Tipo_de_base_map == 0) {
    m <- leaflet() |> 
        addProviderTiles(provider = 'OpenStreetMap') |> 
        addHeatmap(
            lng = Layer$longitude,
            lat = Layer$latitude,
            radius = 15,
            blur = 20,
            max = 0.05
        )
} else if (Tipo_de_base_map == 1) {
    m <- leaflet(data = Layer) |> 
        addProviderTiles(provider = 'OpenStreetMap') |> 
        addMarkers(
            lng = ~longitude, lat = ~latitude,
            label = ~SmoNombre,
            clusterOptions = markerClusterOptions()
        )
}

# Guardamos el HTML
saveWidget(m, Formato_de_salida, selfcontained = FALSE)
