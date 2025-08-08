from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterEnum,
    QgsProcessingParameterDateTime,
    QgsProcessingParameterFeatureSink,
    QgsFeatureSink,
    QgsFeature,
    QgsProject
)
from datetime import datetime

class FiltroPorSmoNombreFechaYDepartamentos(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    FECHA_DESDE = 'FECHA_DESDE'
    FECHA_HASTA = 'FECHA_HASTA'
    DEP_IDS = 'DEP_IDS'
    VALORES = 'VALORES'
    OUTPUT = 'OUTPUT'

    opciones = [ '*NO USAR* OBSTRUCCION CLOACA (SIN DETER)' , 'BUSQUEDA DE ACOMETIDA' ,
    'CAMBIAR TAPA' , 'CONEX DE CLOACA DIAM 110 MM   ' , 'CONEXIONES NUEVA POR CONVENIO' ,
    'HUNDIMIENTO CLOACA' , 'LIMPIEZA' , 'NIVEL BOCA REGISTRO' , 'OBSTRUC. COLECTORA (CLOACA)   ' ,
    'OBSTRUCCION DOMIC.(CLOACA)    ' , 'REPARACION COLECTORA          ' , 'REPARACION CONEX. DOMIC.' , 
    'SOLICITUD DESAGOTE POZO' , 'SOLICITUD REPARACION CLOACA' , ]

    departamentos = ['Capital', 'Rivadavia', 'Santa Lucía','Rawson','Pocito','Zonda','Ullum','Chimbas',
                     '9deJulio','Albardón','Angaco','San Martín','Caucete','25 de Mayo', 'Sarmiento','Calingasta','Iglesia','Jáchal','Valle Fértil']  # DepId: 1, 2, 3

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterDateTime(
                self.FECHA_DESDE,
                'Fecha Recibido desde',
                defaultValue=None
            )
        )

        self.addParameter(
            QgsProcessingParameterDateTime(
                self.FECHA_HASTA,
                'Fecha Recibido hasta',
                defaultValue=None
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.DEP_IDS,
                'Seleccionar Departamentos',
                options=self.departamentos,
                allowMultiple=True
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.VALORES,
                'Seleccionar Motivo de Reclamo',
                options=self.opciones,
                allowMultiple=True
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, 'Filtro Reclamos Cloaca')
        )

    def processAlgorithm(self, parameters, context, feedback):
        layers = QgsProject.instance().mapLayersByName('vw_gra_RecReclamos_Cloaca')
        if not layers:
          raise QgsProcessingException("La capa 'reclamos_cloaca' no está cargada en el proyecto.")
        capa = layers[0]
        
        indices_motivos = self.parameterAsEnums(parameters, self.VALORES, context)
        valores_filtrados = [self.opciones[i] for i in indices_motivos]

        indices_dep = self.parameterAsEnums(parameters, self.DEP_IDS, context)
        dep_ids_validos = [i + 1 for i in indices_dep]  # Capital = 1, Rivadavia = 2, Santa Lucía = 3

        # Extraemos solo la fecha (sin hora)
        fecha_desde = self.parameterAsDateTime(parameters, self.FECHA_DESDE, context).date()
        fecha_hasta = self.parameterAsDateTime(parameters, self.FECHA_HASTA, context).date()

        (sink, output_id) = self.parameterAsSink(
            parameters, self.OUTPUT, context,
            capa.fields(), capa.wkbType(), capa.sourceCrs()
        )

        for f in capa.getFeatures():
            valor_nombre = f['SmoNombre']
            valor_fecha = f['FechaRecibido']
            valor_dep = f['DepId']

            if valor_dep not in dep_ids_validos:
                continue

            if valor_nombre not in valores_filtrados:
                continue

            if not valor_fecha:
                continue

            # Convertimos el valor de FechaRecibido a solo fecha
            if isinstance(valor_fecha, datetime):
                fecha_solo = valor_fecha.date()
            elif hasattr(valor_fecha, 'date'):
                fecha_solo = valor_fecha.date()
            else:
                continue  # formato inválido

            if fecha_desde <= fecha_solo <= fecha_hasta:
                sink.addFeature(f, QgsFeatureSink.FastInsert)
                
        # Renombrar la capa de salida
        fecha_desde_str = fecha_desde.toPyDate().strftime('%Y%m%d')
        fecha_hasta_str = fecha_hasta.toPyDate().strftime('%Y%m%d')
        nuevo_nombre = f'cloaca_{fecha_desde_str}_{fecha_hasta_str}'

        capa_resultado = QgsProject.instance().mapLayer(output_id)
        if capa_resultado:
            capa_resultado.setName(nuevo_nombre)

        return {self.OUTPUT: output_id}

    def name(self):
        return 'filtro_reclamos_cloaca'

    def displayName(self):
        return 'Filtrar Reclamos de Cloaca - OSSE'

    def group(self):
        return 'OSSE'

    def groupId(self):
        return 'mis_scripts'

    def shortHelpString(self):
        return 'Filtra los reclamos de Cloaca por Motivo/s (SmoNombre), Fecha desde (sin hora)(FechaRecibido), Fecha hasta (sin hora)(FechaRecibido) y  Departamento/s de San Juan (DepId). Realizado en OSSE- Departamento TIC- Área Sistemas- Sector SIG por Carlos Tapia '
        
    def createInstance(self):
        return FiltroPorSmoNombreFechaYDepartamentos()
