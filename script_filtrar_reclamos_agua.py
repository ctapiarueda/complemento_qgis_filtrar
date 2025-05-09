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

    opciones = ['*NO USAR*  SIN PRESION', '*NO USAR* ROTURA LLAVE MAESTRA          ' ,
    'AJUSTE DE CLORACION' , 'ANULAR CONEXION               ' , 'BALIZAMIENTO' , 
    'BUSQUEDA VE' , 'CAMBIO DE CONEX. DOMICILIARIA ' , 'CAMBIO DE LLAVE' , 'CAÑO ROTO EN CALLE' ,
    'CAÑO ROTO EN VEREDA' , 'CAÑO ROTO EN VEREDA - PARA MAQUINA' , 'CIERRE DE LL/M                ' ,
    'CLC LLM P/CYR' , 'COLOCACION DE LL PARA CYR' , 'COLOCACIÓN MEDIDOR' , 'COLOCAR LLAVE MAESTRA         ' ,
    'CONEXIONES DE AGUA DIAM 032 MM' , 'CONEXIONES DE AGUA DIAM 20 MM ' , 'CONEXIONES DE AGUA DIAM 25 MM ' , 'DESINFECCIÓN' ,
    'HIDRANTE PARA MAQUINA     ' , 'HUNDIMIENTO AGUA' , 'INSPECCION CONEX CLANDESTINA' , 
    'MEDIDO - GIRAR MEDIDOR' , 'MEDIDO - ODR vereda' , 'MEDIDO - PERDIDA AGUA' , 'ODR CONTRATADA' , 
    'PERDIDA POR CEPO VIOLENTADO' , 'PERDIDA POR RESTRICCION' , 'PIERDE HIDRANTE               ' ,
    'POCA PRESION POR C. y/o REST.' , 'PROFUNDIZAR CONEXION          ' , 'PURGA PROGRAMADA' ,
    'REPARAR VALVULA EXCLUSA       ' , 'SIN AGUA' , 'SIN AGUA - PARA MAQUINA' , 'SOLICITUD DE REPARACION AGUA ' ,
    'SOLICITUD PURGA' , 'TAPAR POZO/RETIRAR ESCOMBRO' ,  'TOMA PRESION PROGRAMADA  ' , 
    'TRA VARIOS                    ' , 'TURBIEDAD' ]

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
            QgsProcessingParameterFeatureSink(self.OUTPUT, 'Capa filtrada')
        )

    def processAlgorithm(self, parameters, context, feedback):
        layers = QgsProject.instance().mapLayersByName('vw_gra_RecReclamos_Agua')
        if not layers:
          raise QgsProcessingException("La capa 'reclamos_agua' no está cargada en el proyecto.")
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

        return {self.OUTPUT: output_id}

    def name(self):
        return 'filtro_reclamos_agua'

    def displayName(self):
        return 'Filtrar Reclamos de Agua - OSSE'

    def group(self):
        return 'Scripts personalizados'

    def groupId(self):
        return 'mis_scripts'

    def shortHelpString(self):
        return 'Filtra los reclamos de Agua por Motivo/s (SmoNombre), Fecha desde (sin hora)(FechaRecibido), Fecha hasta (sin hora)(FechaRecibido) y  Departamento/s de San Juan (DepId). Realizado en OSSE- Departamento TIC- Área Sistemas- Sector SIG por Carlos Tapia '
        

    def createInstance(self):
        return FiltroPorSmoNombreFechaYDepartamentos()
