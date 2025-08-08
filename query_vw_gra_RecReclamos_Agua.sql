CREATE VIEW [dbo].[vw_gra_RecReclamos_Agua] AS
SELECT  g.[RecId]
      ,g.[TavNombre]
      ,g.[RecNombre]
      ,g.[SmoId]
      ,g.[SmoNombre]
      ,g.[RecDiametro]
      ,g.[TmvId]
      ,g.[RecObservaciones]
      ,g.[RecX]
      ,g.[RecY]
      ,g.[FechaRecibido]
      ,g.[FechaGrabado]
      ,g.[FechaConfirmado]
      ,g.[FechaSuprimido]
	  ,geometry::Point(g.RecX, g.RecY, 22192) AS geom
      ,c.[MorId]
      ,c.[MorNombre]
      ,c.[UbrLocalidad]
      ,c.[DepId]
  FROM [Jelu].[dbo].[vwRecReclamosConsultaGeneral] g
  INNER JOIN [Jelu].[dbo].[vwRecReclamosCompletos] c
    ON g.RecId = c.RecId
  WHERE (g.[RecX]>2000000 AND g.[RecY]>6000000 AND
  c.MorId =1)