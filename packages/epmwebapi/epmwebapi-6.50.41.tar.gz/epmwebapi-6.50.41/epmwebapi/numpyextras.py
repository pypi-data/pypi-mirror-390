import base64
from itertools import chain
from typing import Any, Dict, List
from uuid import UUID
import numpy as np
import datetime as dt
import dateutil.parser
import datetime
from datetime import timezone

from .itempathjson import ItemPathJSON
from .basicvariable import DataTypeId

class NumpyExtras:

    def __init__(self):
      self._int = {}
      for i in range(60):
        self._int['{:02}'.format(i)] = i

    def numpyArrayFromDataValues(self, dataValues, sourceDataType = None):
        valuesCount = len(dataValues)
        i = 0

        dataType = float
        if (sourceDataType is not None):
          dataType = self._getDataType(sourceDataType)
        else:
          while (i < valuesCount):
            if ('dataTypeId' in dataValues[i] and dataValues[i]['dataTypeId'] != 'i=' + str(DataTypeId.Unknown.value)):
              dataType = self._getDataType(dataValues[i]['dataTypeId'])
              break
            if (dataValues[i]['value'] is not None):
              dataType = type(dataValues[i]['value'])
              break
            i = i + 1

        numpyArray = self._getNumpyArray(dataType, valuesCount)
        if valuesCount < 1:
            return numpyArray

        import time
        start_time = time.time()

        timestamps = map(self.fastValueToDateTime, [ x['timestamp'] for x in dataValues])
        numpyArray['Timestamp'].flat[:] = list(timestamps)

        numpyArray['Quality'].flat[:] = [ x['quality'] for x in dataValues]

        if dataType == float:
          numpyArray['Value'].flat[:] = list(map(lambda x: (self._getSpecialValue(x['value']) if type(x['value']) == str else x['value']) if x['value'] is not None else np.nan, dataValues))
        elif dataType == int:
          numpyArray['Value'].flat[:] = list(map(lambda x: int(x['value']) if x['value'] is not None else 0, dataValues))
        elif dataType == dt.datetime:
          timestamps = map(self.fastValueToDateTime, [ x['value'] for x in dataValues])
          numpyArray['Value'].flat[:] = list(timestamps)
        else:
          i = 0
          for numpyValue in numpyArray:
            dataValue = dataValues[i]
            if dataValue['value'] is not None:
              numpyValue['Value'] = dataValue['value']
            i = i + 1

        return numpyArray
    
    from numpy.typing import NDArray
    def numpyArrayFromEvents(self, selectFields:List[str], values:List[object], dataTypes:List[str], valueRanks:List[int]) -> NDArray[Any]:
      
      if len(values) < 1:
         return np.empty([0], [])
      
      fieldsMap = {}

      nArrayTypes = []
      index = 0
      for i, field in enumerate(selectFields):
        dataType = dataTypes[i]
        valueRank = valueRanks[i]

        if (field in ['PayloadVariables', 'PayloadValues']):
          continue
        nArrayTypes.append((field, self._inferDType(dataType)))
        fieldsMap[field] = (index, dataType, False)
        index = index + 1

      payload_vars_idx = selectFields.index("PayloadVariables") if "PayloadVariables" in selectFields else -1
      payload_vals_idx = selectFields.index("PayloadValues") if "PayloadValues" in selectFields else -1

      if payload_vars_idx >= 0:
        all_var_names = set(chain.from_iterable(row[payload_vars_idx] if row[payload_vars_idx] else [] for row in values))
        for i, field in enumerate(all_var_names):
           dType = self.get_payload_var_types(field, values, payload_vars_idx, payload_vals_idx)
           fieldsMap[field] = (index, dType, True)
           nArrayTypes.append((field, self._inferDType(dType)))
           nArrayTypes.append((field + "_Timestamp", 'object'))
           nArrayTypes.append((field + "_Quality", 'object'))
           index = index + 3

      numpyArray = np.empty([len(values)], nArrayTypes)

      for fieldName in fieldsMap:
        index = fieldsMap[fieldName][0]
        dataType = fieldsMap[fieldName][1]
        isPayloadField = fieldsMap[fieldName][2]

        if isPayloadField:
          i = 0
          for numpyValue in numpyArray:
            row = values[i]
            dataValue = self.get_payload_var_values(fieldName, row, payload_vars_idx, payload_vals_idx)
            if dataValue is not None:
              if self._isInteger(dataType):
                numpyValue[fieldName] = int(dataValue['value'])
              elif self._isFloat(dataType):
                numpyValue[fieldName] = self._getSpecialValue(dataValue['value'])
              elif self._isDateTime(dataType):
                numpyValue[fieldName] = self.fastValueToDateTime(dataValue['value'])
              elif self._isBoolean(dataType):
                numpyValue[fieldName] = bool(dataValue['value'])
              else:
                numpyValue[fieldName] = dataValue['value']

              numpyValue[fieldName + '_Timestamp'] = self.fastValueToDateTime(dataValue['timestamp'])
              numpyValue[fieldName + '_Quality'] = dataValue['quality']
            i = i + 1
        else:
          if self._isInteger(dataType):
            numpyArray[fieldName].flat[:] = list(map(lambda row: int(row[index]) if row[index] is not None else 0, values))
          elif self._isFloat(dataType):
            numpyArray[fieldName].flat[:] = list(map(lambda row: (self._getSpecialValue(row[index]) if type(row[index]) == str else row[index]) if row[index] is not None else np.nan, values))
          elif self._isDateTime(dataType):
            timestamps = map(self.fastValueToDateTime, [ row[index] for row in values])
            numpyArray[fieldName].flat[:] = list(timestamps)
          elif self._isNodeId(dataType):
            numpyArray[fieldName].flat[:] = list(map(lambda row: ItemPathJSON('OPCUA.NodeId', None, row[index]) if row[index] is not None else None, values))
          elif self._isByteString(dataType):
            numpyArray[fieldName].flat[:] = list(map(lambda row: self.clsid_to_uuid(row[index]) if row[index] is not None else None, values))
          else:
            i = 0
            for numpyValue in numpyArray:
              row = values[i]
              if row[index] is not None:
                numpyValue[fieldName] = row[index]
              i = i + 1

      return numpyArray


    def _getSpecialValue(self, value):
      from .epmvariable import InfinityName, MinusInfinityName, NanName
      if value == InfinityName:
         return np.inf
      elif value == MinusInfinityName:
        return -np.inf
      elif value == NanName:
        return np.nan
      return value


    def _getDataType(self, dataType:str) -> type:
      if (dataType == "i="+str(DataTypeId.Bit.value)):
        return bool
      elif (dataType == "i="+str(DataTypeId.DateTime.value)):
        return dt.datetime
      elif (dataType == "i="+str(DataTypeId.Double.value) or 
            dataType == "i="+str(DataTypeId.Float.value)):
        return float
      elif (dataType == "i="+str(DataTypeId.Int.value)):
        return int
      elif (dataType == "i="+str(DataTypeId.UInt.value)):
        return int
      elif (dataType == "i="+str(DataTypeId.String.value)):
        return str
      elif (dataType == "i="+str(DataTypeId.NodeId.value)):
          return ItemPathJSON
      elif (dataType == "i="+str(DataTypeId.ByteString.value)):
          return UUID
      return float
    
    def _inferDType(self, dataType:str):
        if (self._isBoolean(dataType)):
          return 'bool'  
        elif (self._isFloat(dataType)):
          return '>f4'
        elif (self._isInteger(dataType)):
          return '>i8'
        else:
          return 'object'     

    def _isInteger(self, dataType:str):
       return (dataType == "i="+str(DataTypeId.Int.value) or dataType == "i="+str(DataTypeId.UInt.value))

    def _isFloat(self, dataType:str):
       return (dataType == "i="+str(DataTypeId.Double.value) or dataType == "i="+str(DataTypeId.Float.value))
    
    def _isBoolean(self, dataType:str):
       return (dataType == "i="+str(DataTypeId.Bit.value))

    def _isDateTime(self, dataType:str):
       return (dataType == "i="+str(DataTypeId.DateTime.value))
    
    def _isNodeId(self, dataType:str):
       return (dataType == "i="+str(DataTypeId.NodeId.value))

    def _isByteString(self, dataType:str):
       return (dataType == "i="+str(DataTypeId.ByteString.value))

    def clsid_to_uuid(self, clsid_b64: str) -> UUID:
      try:
          # Decodificar a string Base64
          clsid_bytes = base64.b64decode(clsid_b64)
          
          # Verificar se o tamanho é 16 bytes (tamanho de um UUID/GUID)
          if len(clsid_bytes) != 16:
              raise ValueError(f"CLSID decodificado tem {len(clsid_bytes)} bytes, esperado 16 bytes para UUID")
          
          # Criar UUID a partir dos bytes
          # Os bytes de um CLSID seguem a ordem little-endian para os primeiros campos
          # Reorganizar para o formato UUID (big-endian)
          uuid_bytes = (
              clsid_bytes[3::-1] +  # Data1 (4 bytes, invertido)
              clsid_bytes[5:3:-1] +  # Data2 (2 bytes, invertido)
              clsid_bytes[7:5:-1] +  # Data3 (2 bytes, invertido)
              clsid_bytes[8:]  # Data4 (8 bytes, sem alteração)
          )
          
          # Converter para UUID
          return UUID(bytes=uuid_bytes)
      
      except base64.binascii.Error:
          raise ValueError("String Base64 inválida")
      except Exception as e:
          raise ValueError(f"Erro ao converter CLSID para UUID: {str(e)}")

    def get_payload_var_types(self, fieldName:str, values: List[List[Any]], payload_vars_idx: int, payload_vals_idx: int) -> str:
      var_types = {}
      for row in values:
        fieldIndex = row[payload_vars_idx].index(fieldName) if row[payload_vars_idx] else []
        if fieldIndex == -1:
          continue
        val = row[payload_vals_idx][fieldIndex] if row[payload_vals_idx] else []
        if val is None:
           continue
        return val["dataTypeId"]
      
    def get_payload_var_values(self, fieldName:str, row: List[Any], payload_vars_idx: int, payload_vals_idx: int) -> Any:
        fieldIndex = row[payload_vars_idx].index(fieldName) if row[payload_vars_idx] else []
        if fieldIndex == -1:
          return None
        return row[payload_vals_idx][fieldIndex] if row[payload_vals_idx] else []

    def _getNumpyArray(self, dataType, valuesCount):
        if dataType == int:
            return np.empty([valuesCount], dtype=np.dtype([('Value', '>i8'), ('Timestamp', 'object'), ('Quality', 'object')]))
        elif dataType == float:
            return np.empty([valuesCount], dtype=np.dtype([('Value', '>f4'), ('Timestamp', 'object'), ('Quality', 'object')]))
        elif dataType == bool:
            return np.empty([valuesCount], dtype=np.dtype([('Value', 'bool'), ('Timestamp', 'object'), ('Quality', 'object')]))
        elif dataType == str:
            return np.empty([valuesCount], dtype=np.dtype([('Value', 'object'), ('Timestamp', 'object'), ('Quality', 'object')]))
        elif dataType == dt.datetime:
            return np.empty([valuesCount], dtype=np.dtype([('Value', 'object'), ('Timestamp', 'object'), ('Quality', 'object')]))
        else: 
            return np.empty([valuesCount], dtype=np.dtype([('Value', '>f8'), ('Timestamp', 'object'), ('Quality', 'object')]))

    def fastValueToDateTime(self, item) -> datetime.datetime:
      val = item
      l = len(val)
      if (l == 23 or l == 24): #format == "%Y-%m-%dT%H:%M:%S.%fZ" and 
          us = int(val[20:(l - 1)])
          # If only milliseconds are given we need to convert to microseconds.
          if l == 23:
              us *= 10000
          if l == 24:
              us *= 1000
          return datetime.datetime(*map(int, [val[0:4], val[5:7], val[8:10], val[11:13], val[14:16], val[17:19]]), us, tzinfo=timezone.utc
          )
      elif (l == 20): #format == "%Y-%m-%dT%H:%M:%SZ" and 
          return datetime.datetime(*map(int, [val[0:4], val[5:7], val[8:10], val[11:13], val[14:16], val[17:19]]), 0, tzinfo=timezone.utc)
      else:
        return dateutil.parser.parse(val).astimezone(timezone.utc)

    def getDictValue(self, value):
      if value in self._int:
        return self._int[value]
      value = int(value)
      self._int[value] = value
      return value

