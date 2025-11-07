from ._swordfishcpp import sw_is_ce_edition  # type: ignore
if not sw_is_ce_edition():
    from ._swordfishcpp import (  # type: ignore
        _bondCashflow, _bondConvexity, _bondDirtyPrice, _bondDuration, _bondYield,
        _brentq, _brute, _cds, _condValueAtRisk, _crmwCBond, _cubicSpline,
        _cubicSplinePredict, _cummdd, _fmin, _fminBFGS, _fminLBFGSB, _fminNCG,
        _fminSLSQP, _gaussianKde, _gaussianKdePredict, _irs, _kroghInterpolate,
        _kroghInterpolateFit, _linearInterpolateFit, _linprog, _maxDrawdown, _mdd, _ns,
        _nss, _nssPredict, _osqp, _piecewiseLinFit, _polyFit, _polyPredict,
        _pwlfPredict, _qclp, _quadprog, _scs, _socp, _solve, _treasuryConversionFactor,
        _trueRange, _valueAtRisk, _vanillaOption, _varma
    )

from ._swordfishcpp import (  # type: ignore
    _abs, _accumulate, _acf, _acos, _acosh, _adaBoostClassifier, _adaBoostRegressor,
    _add, _addColumn, _addRangePartitions, _addValuePartitions, _addVolumes, _adfuller,
    _aggrTopN, _aj, _align, _all, _and, _anova, _any, _append_, _appendTuple_, _array,
    _arrayVector, _asFreq, _asin, _asinh, _asis, _asof, _at, _atImax, _atImin, _atan,
    _atanh, _autocorr, _avg
)
from ._swordfishcpp import (  # type: ignore
    _backup, _backupDB, _backupSettings, _backupTable, _bar, _base64Decode,
    _base64Encode, _beta, _between, _bfill_, _bigarray, _binaryExpr, _binsrch, _bitAnd,
    _bitOr, _bitXor, _blob, _bondAccrInt, _bool, _bucket, _bucketCount, _businessDay,
    _businessMonthBegin, _businessMonthEnd, _businessQuarterBegin, _businessQuarterEnd,
    _businessYearBegin, _businessYearEnd, _byColumn, _byRow
)
from ._swordfishcpp import (  # type: ignore
    _cacheDS_, _cacheDSNow, _call, _cast, _cbrt, _cdfBeta, _cdfBinomial, _cdfChiSquare,
    _cdfExp, _cdfF, _cdfGamma, _cdfKolmogorov, _cdfLogistic, _cdfNormal, _cdfPoisson,
    _cdfStudent, _cdfUniform, _cdfWeibull, _cdfZipf, _ceil, _cell, _cells, _char,
    _charAt, _checkBackup, _chiSquareTest, _cholesky, _cj, _clear_, _clearAllCache,
    _clearAllIOTDBLatestKeyCache, _clearAllIOTDBStaticTableCache,
    _clearAllTSDBSymbolBaseCache, _clearDSCache_, _clearDSCacheNow, _clip, _clip_,
    _coalesce, _coevent, _coint, _col, _cols, _columnNames, _complex, _compress,
    _concat, _concatDateTime, _concatMatrix, _conditionalFilter, _conditionalIterate,
    _constantDesc, _contextCount, _contextSum, _contextSum2, _contextby,
    _convertEncode, _convertExcelFormula, _convertTZ, _copy, _corr, _corrMatrix, _cos,
    _cosh, _count, _countNanInf, _covar, _covarMatrix, _crc32, _cross, _crossStat,
    _cumPositiveStreak, _cumavg, _cumbeta, _cumcorr, _cumcount, _cumcovar,
    _cumfirstNot, _cumlastNot, _cummax, _cummed, _cummin, _cumnunique, _cumpercentile,
    _cumprod, _cumrank, _cumstd, _cumstdp, _cumsum, _cumsum2, _cumsum3, _cumsum4,
    _cumvar, _cumvarp, _cumwavg, _cumwsum, _cut, _cutPoints
)
from ._swordfishcpp import (  # type: ignore
    _dailyAlignedBar, _date, _datehour, _datetime, _dayOfMonth, _dayOfWeek, _dayOfYear,
    _daysInMonth, _decimal128, _decimal32, _decimal64, _decimalFormat,
    _decimalMultiply, _decodeShortGenomeSeq, _decompress, _deepCopy, _defined, _defs,
    _deg2rad, _deltas, _dema, _demean, _denseRank, _derivative, _det, _diag, _dict,
    _dictUpdate_, _difference, _differentialEvolution, _digitize,
    _disableActivePartition, _disableTSDBAsyncSorting, _distance, _distinct, _div,
    _dividedDifference, _dot, _double, _drop, _dropColumns_, _dropPartition, _dropna,
    _duration, _dynamicGroupCumcount, _dynamicGroupCumsum
)
from ._swordfishcpp import (  # type: ignore
    _each, _eachAt, _eachLeft, _eachPost, _eachPre, _eachRight, _eig, _ej, _elasticNet,
    _elasticNetCV, _ema, _enableActivePartition, _enableTSDBAsyncSorting,
    _encodeShortGenomeSeq, _endsWith, _enlist, _eq, _eqFloat, _eqObj, _eqPercent,
    _erase_, _esd, _euclidean, _eval, _ewmCorr, _ewmCov, _ewmMean, _ewmStd, _ewmVar,
    _exists, _exp, _exp2, _expm1, _expr, _extractTextSchema, _eye
)
from ._swordfishcpp import (  # type: ignore
    _fTest, _ffill, _ffill_, _fill_, _find, _first, _firstHit, _firstNot,
    _fixedLengthArrayVector, _fj, _flatten, _flip, _floor, _flushOLAPCache,
    _flushTSDBCache, _form, _format, _fromJson, _fromStdJson, _fromUTF8, _funcByName,
    _fy5253, _fy5253Quarter
)
from ._swordfishcpp import (  # type: ignore
    _garch, _gaussianNB, _ge, _gema, _genShortGenomeSeq, _genericStateIterate,
    _genericTStateIterate, _getBackupList, _getBackupMeta, _getBackupStatus,
    _getChunkPath, _getChunksMeta, _getLevelFileIndexCacheStatus,
    _getLicenseExpiration, _getMemoryStat, _getOLAPCacheEngineStat,
    _getOLAPCachedSymbolBaseMemSize, _getPKEYCompactionTaskStatus, _getPKEYMetaData,
    _getRecoveryTaskStatus, _getTSDBCachedSymbolBaseMemSize,
    _getTSDBCompactionTaskStatus, _getTSDBDataStat, _getTSDBMetaData,
    _getTSDBTableIndexCacheStatus, _getTablet, _getTabletsMeta, _glm, _gmm, _gmtime,
    _gram, _gramSchmidt, _groupby, _groups, _gt
)
from ._swordfishcpp import (  # type: ignore
    _hasNull, _hashBucket, _head, _hex, _highDouble, _highLong, _histogram2d, _hour,
    _hourOfDay
)
from ._swordfishcpp import (  # type: ignore
    _ifNull, _ifValid, _ifirstHit, _ifirstNot, _iif, _ilastNot, _ilike, _imax,
    _imaxLast, _imin, _iminLast, _imr, _in, _indexedSeries, _indexedTable, _initcap,
    _int, _int128, _integral, _interpolate, _intersection, _interval, _invBeta,
    _invBinomial, _invChiSquare, _invExp, _invF, _invGamma, _invLogistic, _invNormal,
    _invPoisson, _invStudent, _invUniform, _invWeibull, _inverse, _ipaddr, _isAlNum,
    _isAlpha, _isDigit, _isDuplicated, _isIndexedMatrix, _isIndexedSeries, _isLeapYear,
    _isLower, _isMonotonic, _isMonotonicDecreasing, _isMonotonicIncreasing,
    _isMonthEnd, _isMonthStart, _isNanInf, _isNothing, _isNull, _isNumeric,
    _isOrderedDict, _isPeak, _isQuarterEnd, _isQuarterStart, _isSorted, _isSpace,
    _isTitle, _isUpper, _isValid, _isValley, _isVoid, _isYearEnd, _isYearStart, _isort,
    _isort_, _isortTop, _iterate
)
from ._swordfishcpp import (  # type: ignore
    _join, _join_, _jsonExtract
)
from ._swordfishcpp import (  # type: ignore
    _kama, _kendall, _keyedStreamTable, _keyedTable, _keys, _kmeans, _knn, _ksTest,
    _kurtosis
)
from ._swordfishcpp import (  # type: ignore
    _lasso, _lassoBasic, _lassoCV, _last, _lastNot, _lastWeekOfMonth,
    _latestIndexedTable, _latestKeyedStreamTable, _latestKeyedTable, _le, _left,
    _lfill, _lfill_, _license, _like, _linearTimeTrend, _lj, _loadBackup, _loadModel,
    _loadNpy, _loadNpz, _loadRecord, _loadTable, _loadText, _loadTextEx, _loc,
    _localtime, _loess, _log, _log10, _log1p, _log2, _logisticRegression, _long, _loop,
    _lowDouble, _lowLong, _lowRange, _lower, _lowerBound, _lpad, _lshift, _lsj, _lt,
    _ltrim, _lu
)
from ._swordfishcpp import (  # type: ignore
    _mLowRange, _mTopRange, _ma, _mad, _makeCall, _makeKey, _makeSortedKey,
    _makeUnifiedCall, _mannWhitneyUTest, _manova, _mask, _matrix, _mavg, _mavgTopN,
    _max, _maxIgnoreNull, _maxPositiveStreak, _mbeta, _mbetaTopN, _mcorr, _mcorrTopN,
    _mcount, _mcovar, _mcovarTopN, _md5, _mean, _med, _mem, _member, _memberModify_,
    _merge, _mfirst, _mfirstNot, _microsecond, _mifirstNot, _migrate, _milastNot,
    _millisecond, _mimax, _mimaxLast, _mimin, _miminLast, _min, _minIgnoreNull,
    _minute, _minuteOfHour, _mkurtosis, _mlast, _mlastNot, _mmad, _mmax,
    _mmaxPositiveStreak, _mmed, _mmin, _mmse, _mod, _mode, _month, _monthBegin,
    _monthEnd, _monthOfYear, _move, _moveHotDataToColdVolume, _moving,
    _movingTopNIndex, _movingWindowIndex, _mpercentile, _mpercentileTopN, _mprod, _mr,
    _mrank, _mskew, _mslr, _mstd, _mstdTopN, _mstdp, _mstdpTopN, _msum, _msum2,
    _msumTopN, _mul, _multiTableRepartitionDS, _multinomialNB, _mutualInfo, _mvar,
    _mvarTopN, _mvarp, _mvarpTopN, _mwavg, _mwsum, _mwsumTopN
)
from ._swordfishcpp import (  # type: ignore
    _nanInfFill, _nanosecond, _nanotime, _nanotimestamp, _ne, _neg, _neville, _next,
    _nextState, _norm, _normal, _not, _now, _nullCompare, _nullFill, _nullFill_,
    _nullIf, _nunique
)
from ._swordfishcpp import (  # type: ignore
    _objByName, _objectChecksum, _objs, _ols, _olsEx, _oneHot, _or
)
from ._swordfishcpp import (  # type: ignore
    _pack, _pair, _panel, _parseExpr, _parseInt, _parseInteger, _parseJsonTable,
    _partial, _partition, _pca, _pcall, _pcross, _percentChange, _percentile,
    _percentileRank, _pivot, _pj, _ploadText, _ploop, _point, _poly1d, _polynomial,
    _pop_, _pow, _predict, _prev, _prevState, _print, _prod, _push_, _pwj
)
from ._swordfishcpp import (  # type: ignore
    _qr, _quantile, _quantileSeries, _quarterBegin, _quarterEnd
)
from ._swordfishcpp import (  # type: ignore
    _rad2deg, _rand, _randBeta, _randBinomial, _randChiSquare, _randDiscrete, _randExp,
    _randF, _randGamma, _randLogistic, _randMultivariateNormal, _randNormal,
    _randPoisson, _randStudent, _randUniform, _randWeibull, _randomForestClassifier,
    _randomForestRegressor, _rank, _ratio, _ratios, _rdp, _reciprocal, _reduce,
    _refCount, _regexCount, _regexFind, _regexFindStr, _regexReplace, _regroup,
    _remoteRun, _remoteRunCompatible, _remoteRunWithCompression, _removeHead_,
    _removeTail_, _rename_, _renameTable, _reorderColumns_, _repartitionDS, _repeat,
    _replace, _replace_, _replaceColumn_, _replay, _replayDS, _repmat, _resample,
    _reshape, _residual, _restore, _restoreDB, _restoreTable, _reverse, _ridge,
    _ridgeBasic, _right, _rolling, _rollingPanel, _round, _row, _rowAlign, _rowAnd,
    _rowAt, _rowAvg, _rowBeta, _rowCorr, _rowCount, _rowCovar, _rowDenseRank, _rowDot,
    _rowEuclidean, _rowGroupby, _rowImax, _rowImaxLast, _rowImin, _rowIminLast,
    _rowKurtosis, _rowMax, _rowMin, _rowMove, _rowNames, _rowNext, _rowNo, _rowOr,
    _rowPrev, _rowProd, _rowRank, _rowSize, _rowSkew, _rowStd, _rowStdp, _rowSum,
    _rowSum2, _rowTanimoto, _rowVar, _rowVarp, _rowWavg, _rowWsum, _rowXor, _rows,
    _rpad, _rshift, _rtrim
)
from ._swordfishcpp import (  # type: ignore
    _sample, _saveAsNpy, _saveDatabase, _saveDualPartition, _saveModel, _savePartition,
    _saveTable, _saveText, _saveTextFile, _schema, _schur, _searchK, _seasonalEsd,
    _second, _secondOfMinute, _segment, _segmentby, _sej, _sem, _semiMonthBegin,
    _semiMonthEnd, _seq, _sessionWindow, _set, _setColumnComment, _setIndexedMatrix_,
    _setIndexedSeries_, _setRandomSeed, _setRetentionPolicy, _shape, _shapiroTest,
    _share, _short, _shuffle, _shuffle_, _signbit, _signum, _sin, _sinh, _size, _skew,
    _sleep, _slice, _sliceByKey, _sma, _snippet, _sort, _sort_, _sortBy_, _spearmanr,
    _splev, _spline, _split, _splrep, _sql, _sqlCol, _sqlColAlias, _sqlDS, _sqlDelete,
    _sqlUpdate, _sqrt, _square, _startsWith, _stat, _stateIterate, _std, _stdp, _stl,
    _strReplace, _streamTable, _stretch, _string, _stringFormat, _strip, _strlen,
    _strlenu, _strpos, _sub, _subarray, _substr, _substru, _subtuple, _sum, _sum2,
    _sum3, _sum4, _sumbars, _summary, _svd, _symbol, _symbolCode, _symmetricDifference,
    _syncDict, _syntax
)
from ._swordfishcpp import (  # type: ignore
    _t3, _tTest, _table, _tableInsert, _tableUpsert, _tail, _take, _talib, _talibNull,
    _tan, _tanh, _tanimoto, _tema, _temporalAdd, _temporalFormat, _temporalParse,
    _temporalSeq, _tensor, _textChunkDS, _til, _time, _timestamp, _tmLowRange,
    _tmTopRange, _tmavg, _tmbeta, _tmcorr, _tmcount, _tmcovar, _tmfirst, _tmkurtosis,
    _tmlast, _tmmax, _tmmed, _tmmin, _tmove, _tmoving, _tmpercentile, _tmprod, _tmrank,
    _tmskew, _tmstd, _tmstdp, _tmsum, _tmsum2, _tmvar, _tmvarp, _tmwavg, _tmwsum,
    _toCharArray, _toJson, _toStdJson, _toUTF8, _today, _topRange, _transDS_,
    _transFreq, _transpose, _triggerTSDBCompaction, _tril, _trim, _trima, _triu,
    _truncate, _tupleSum, _twindow, _type, _typestr
)
from ._swordfishcpp import (  # type: ignore
    _undef, _ungroup, _unifiedCall, _unifiedExpr, _union, _unionAll, _unpack, _unpivot,
    _update_, _updateLicense, _upper, _upsert_, _uuid
)
from ._swordfishcpp import (  # type: ignore
    _valueChanged, _values, _var, _varp, _vectorAR, _vectorNorm, _version, _volumeBar
)
from ._swordfishcpp import (  # type: ignore
    _wavg, _wc, _wcovar, _weekBegin, _weekEnd, _weekOfMonth, _weekOfYear, _weekday,
    _wilder, _window, _winsorize, _winsorize_, _withNullFill, _wj, _wls, _wma,
    _writeLog, _writeLogLevel, _wsum
)
from ._swordfishcpp import (  # type: ignore
    _xdb, _xor
)
from ._swordfishcpp import (  # type: ignore
    _year, _yearBegin, _yearEnd
)
from ._swordfishcpp import (  # type: ignore
    _zTest, _zigzag, _zscore
)

from ._function_tools import builtin_function
from ._swordfishcpp import Constant, Void   # type: ignore
from ._helper import Alias
from typing import Literal, Union


DFLT = Void.DFLT_VALUE
VOID = Void.VOID_VALUE


@builtin_function(_abs)
def abs(X: Constant) -> Constant:
    r"""Return the element-by-element absolute value(s) of X.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix/dictionary/table.
    """
    ...


@builtin_function(_accumulate)
def accumulate(func: Constant, X: Constant, init: Constant = DFLT, assembleRule: Union[Alias[Literal["consistent"]], Constant] = DFLT) -> Constant:
    r"""The accumulate template applies func to init and X for accumulating iteration
    (i.e. the result of an iteration is passed forward to the next). Unlike the template
    reduce that returns only the last result, the template accumulate outputs result of each iteration.

    Parameters
    ----------
    func : Constant
        A function for iteration.
    X : Constant
        Data or iteration rule.
    init : Constant, optional
        The initial value to be passed to func, by default DFLT.
    assembleRule : Union[Alias[Literal["consistent"]], Constant], optional
        Indicates how the results of sub-tasks are merged into the final result.
        It accepts either an integer or a string, by default DFLT.
    """
    ...


@builtin_function(_acf)
def acf(X: Constant, maxLag: Constant) -> Constant:
    r"""Calculate the autocorrelation of X from lag=1 to lag=maxLag.

    Parameters
    ----------
    X : Constant
        A vector
    maxLag : Constant
        A positive integer.
    """
    ...


@builtin_function(_acos)
def acos(X: Constant) -> Constant:
    r"""The inverse cosine function.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_acosh)
def acosh(X: Constant) -> Constant:
    r"""The inverse hyperbolic cosine function.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_adaBoostClassifier)
def adaBoostClassifier(ds: Constant, yColName: Constant, xColNames: Constant, numClasses: Constant, maxFeatures: Constant = DFLT, numTrees: Constant = DFLT, numBins: Constant = DFLT, maxDepth: Constant = DFLT, minImpurityDecrease: Constant = DFLT, learningRate: Constant = DFLT, algorithm: Constant = DFLT, randomSeed: Constant = DFLT) -> Constant:
    r"""Fit an AdaBoost classification model.

    Parameters
    ----------
    ds : Constant
        The data sources to be trained. It can be generated with function sqlDS.
    yColName : Constant
        A string indicating the name of the category column in the data sources.
    xColNames : Constant
        A string scalar/vector indicating the names of the feature columns in the data sources.
    numClasses : Constant
        A positive integer indicating the number of categories in the category column.
    maxFeatures : Constant, optional
        An integer or a floating number indicating the number of features to consider
        when looking for the best split, by default DFLT.
    numTrees : Constant, optional
        A positive integer indicating the number of trees, by default DFLT.
    numBins : Constant, optional
        A positive integer indicating the number of bins used when discretizing
        continuous features, by default DFLT.
    maxDepth : Constant, optional
        A positive integer indicating the maximum depth of a tree, by default DFLT.
    minImpurityDecrease : Constant, optional
        A node will be split if this split induces a decrease of the Gini impurity
        greater than or equal to this value, by default DFLT.
    learningRate : Constant, optional
        A positive floating number indicating the contribution of a regressor to the
        next regressor, by default DFLT.
    algorithm : Constant, optional
        A string indicating the algorithm used, by default DFLT.
    randomSeed : Constant, optional
        The seed used by the random number generator, by default DFLT.
    """
    ...


@builtin_function(_adaBoostRegressor)
def adaBoostRegressor(ds: Constant, yColName: Constant, xColNames: Constant, maxFeatures: Constant = DFLT, numTrees: Constant = DFLT, numBins: Constant = DFLT, maxDepth: Constant = DFLT, minImpurityDecrease: Constant = DFLT, learningRate: Constant = DFLT, loss: Constant = DFLT, randomSeed: Constant = DFLT) -> Constant:
    r"""Fit an AdaBoost regression model.

    Parameters
    ----------
    ds : Constant
        Tthe data sources to be trained. It can be generated with function sqlDS.
    yColName : Constant
        A string indicating the name of the dependent variable column in the data sources.
    xColNames : Constant
        A string scalar/vector indicating the names of the feature columns in the data sources.
    maxFeatures : Constant, optional
        An integer or a floating number indicating the number of features to consider
        when looking for the best split, by default DFLT.
    numTrees : Constant, optional
        A positive integer indicating the number of trees, by default DFLT.
    numBins : Constant, optional
        A positive integer indicating the number of bins used when discretizing
        continuous features, by default DFLT.
    maxDepth : Constant, optional
        A positive integer indicating the maximum depth of a tree, by default DFLT.
    minImpurityDecrease : Constant, optional
        A node will be split if this split induces a decrease of impurity greater
        than or equal to this value, by default DFLT.
    learningRate : Constant, optional
        A positive floating number indicating the contribution of a regressor to the
        next regressor, by default DFLT.
    loss : Constant, optional
        A string indicating the loss function to use when updating the weights after
        each boosting iteration, by default DFLT.
    randomSeed : Constant, optional
        The seed used by the random number generator, by default DFLT.
    """
    ...


@builtin_function(_add)
def add(X: Constant, Y: Constant) -> Constant:
    r"""Return the element-by-element sum of X and Y.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix. If X or Y is a pair/vector/matrix
    Y : Constant
        A scalar/pair/vector/matrix. If X or Y is a pair/vector/matrix
    """
    ...


@builtin_function(_addColumn)
def addColumn(table: Constant, colNames: Constant, colTypes: Constant) -> Constant:
    r"""Add a column or columns to a table. It is the only way to add a column to a
    stream table, a DFS table, or a dimension table.

    Parameters
    ----------
    table : Constant
        A table of any type, including an in-memory table, a stream table, a DFS table,
        or a dimension table.
    colNames : Constant
        A STRING scalar/vector indicating the name(s) of the column(s) to be added.
    colTypes : Constant
        A calar/vector indicating the data type(s) of the column(s) to be added.
    """
    ...


@builtin_function(_addRangePartitions)
def addRangePartitions(dbHandle: Constant, newRanges: Constant, level: Constant = DFLT, locations: Constant = DFLT) -> Constant:
    r"""Append new values to the partition scheme of a database. This database must be
    of RANGE domain or of COMPO domain with at least one level of RANGE domain.

    Parameters
    ----------
    dbHandle : Constant
        A database handle.
    newRanges : Constant
        A vector indicating new partitions.
    level : Constant, optional
        A non-negative integer., by default DFLT.
    locations : Constant, optional
        A STRING scalar/vector, by default DFLT.
    """
    ...


@builtin_function(_addValuePartitions)
def addValuePartitions(dbHandle: Constant, newValues: Constant, level: Constant = DFLT, locations: Constant = DFLT) -> Constant:
    r"""Append new values to the partition scheme of a database.

    Parameters
    ----------
    dbHandle : Constant
        A database handle.
    newValues : Constant
        A scalar or vector indicating new partitions.
    level : Constant, optional
        A non-negative integer, by default DFLT.
    locations : Constant, optional
        A STRING scalar/vector, by default DFLT.
    """
    ...


@builtin_function(_addVolumes)
def addVolumes(volumes: Constant) -> Constant:
    r"""Dynamically add volume(s) without rebooting the cluster.

    Parameters
    ----------
    volumes : Constant
        A STRING scalar or vector indicating the volume path(s).
    """
    ...


@builtin_function(_adfuller)
def adfuller(X: Constant, maxLag: Constant = DFLT, regression: Constant = DFLT, autoLag: Constant = DFLT, store: Constant = DFLT, regResults: Constant = DFLT) -> Constant:
    r"""Perform Augmented Dickey-Fuller unit root test.

    Parameters
    ----------
    X : Constant
        A numeric vector indicating the time series data to test.
    maxLag : Constant, optional
        A non-negative integer indicating the maximum lag which is included in test, by default DFLT.
    regression : Constant, optional
        A string indicating the constant and trend order to include in regression, by default DFLT.
    autoLag : Constant, optional
        A string indicating the method to use when automatically determining the lag
        length among the values 0, 1, …, maxlag, by default DFLT.
    store : Constant, optional
        A Boolean value, by default DFLT.
    regResults : Constant, optional
        A Boolean value, by default DFLT.

    Returns
    -------
    Constant
        A dictionary.
    """
    ...


@builtin_function(_aggrTopN)
def aggrTopN(func: Constant, funcArgs: Constant, sortingCol: Constant, top: Constant, ascending: Constant = DFLT) -> Constant:
    r"""After sorting funcArgs based on sortingCol, aggrTopN applies func to the first
    top elements in funcArgs.

    Parameters
    ----------
    func : Constant
        An aggregate function.
    funcArgs : Constant
        The parameters of func. It can be a scalar or vector. It is a tuple if there
        are more than 1 parameter of func.
    sortingCol : Constant
        A numeric/temporal vector, based on which funcArgs are sorted.
    top : Constant
        An integer or floating-point number.

        - If it is an integer, select the first top rows of records for calculation.

        - If it is a floating-point number, the value should be less than 1.0 to indicate a percentage.
          The function will select top of the rows in funcArgs for calculation.
          If the result is less than 1, select the first row. If the result is not an integer,
          it is rounded down and at least one row is selected.
    ascending : Constant, optional
        A Boolean value, by default DFLT
    """
    ...


@builtin_function(_aj)
def aj(leftTable: Constant, rightTable: Constant, matchingCols: Constant, rightMatchingCols: Constant = DFLT) -> Constant:
    r"""The asof join function is used in non-synchronous join. It is similar to the
    left join function with the following differences:

    - Assume the last matching column is "time". For a row in the left table with time=t,
      among the rows in the right table that match all other matching columns,
      if there is not a record with time=t, select the last row before time=t.

    - If there is only 1 joining column, the asof join function assumes the right
      table is sorted on the joining column. If there are multiple joining columns,
      the asof join function assumes the right table is sorted on the last joining
      column within each group defined by the other joining columns. The right table
      does not need to be sorted by the other joining columns. If these conditions are not met,
      unexpected results may be returned. The left table does not need to be sorted.

    .. note::

        - If the left table of asof join is not a DFS table, its right table cannot be
          a DFS table either.

        - The data type of the last matching column is usually of temporal types.
          It can also be of integral types, UUID or IPADDR type.

        - If either the left table or the right table is a partitioned table, the joining
          columns except the last one must include all of the partitioning columns
          of the partitioned tables.

    Parameters
    ----------
    leftTable : Constant
        A table
    rightTable : Constant
        A table
    matchingCols : Constant
        A STRING scalar/vector indicating matching columns.
    rightMatchingCols : Constant, optional
        A STRING scalar/vector indicating all the matching columns in *rightTable*, by default DFLT.
        This argument must be specified if at least one of the matching columns has
        different names in *leftTable* and *rightTable*. The joining column names in
        the result will be the joining column names from the left table.
    """
    ...


@builtin_function(_align)
def align(left: Constant, right: Constant, how: Constant = DFLT, byRow: Constant = DFLT, view: Constant = DFLT) -> Constant:
    r"""Align the left and right matrices based on row labels and/or column labels
    (specified by byRow) using the join method specified by how.

    Parameters
    ----------
    left : Constant
        Matrix with column and/or row labels
    right : Constant
        Matrix with column and/or row labels
    how : Constant, optional
        A STRING scalar indicating the join method with which the two matrices are aligned,
        by default DFLT. The matrices are aligned on the column labels and/or row labels.
        It can be 'outer' (or 'fj'), 'inner' (or 'ej'), 'left' (or 'lj') or 'asof ('aj')'.
        The default value is 'outer', indicating outer join.
    byRow : Constant, optional
        A Boolean or null value, by default DFLT.

        - true: align the matrices on row labels.

        - false: align the matrices on the column labels.

        - Null value (default): align on the row labels and the column labels.
          Specify how in the format of "<row_alignment>,<column alignment>", e.g., how="outer,inner". Do not add a space or special character before or after the comma. If the same alignment method is used on rows and columns, it only needs to be specified once, e.g., how="inner".
    view : Constant, optional
        A Boolean value, by default DFLT

    Returns
    -------
    Constant
        A tuple with 2 aligned matrices.
    """
    ...


@builtin_function(_all)
def all(obj: Union[Alias[Literal["func"]], Constant], *args) -> Constant:
    r"""Return 0 if at least one element of X is false or 0; return 1 otherwise. Null values are ignored.

    Parameters
    ----------
    obj : Union[Alias[Literal[&quot;func&quot;]], Constant]
        A scalar/pair/vector/matrix
    """
    ...


@builtin_function(_and)
def And(X: Constant, Y: Constant) -> Constant:
    r"""Return the element-by-element logical X AND Y.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix.
    Y : Constant
        A scalar/pair/vector/matrix.
    """
    ...


@builtin_function(_anova)
def anova(X: Constant) -> Constant:
    r"""Conduct one-way analysis of variance (ANOVA). Each column in X is a group.

    Parameters
    ----------
    X : Constant
        A matrix or a table with numeric columns.

    Returns
    -------
    Constant
        A dictionary
    """
    ...


@builtin_function(_any)
def any(obj: Union[Alias[Literal["func"]], Constant], *args) -> Constant:
    r"""Return 1 if there is at least one element in X that is true or not 0.

    Parameters
    ----------
    obj : Union[Alias[Literal[&quot;func&quot;]], Constant]
        A scalar/pair/vector/matrix.
    """
    ...


@builtin_function(_append_)
def append_(obj: Constant, newData: Constant) -> Constant:
    r"""Append newData to obj.

    Parameters
    ----------
    obj : Constant
        A vector/tuple/matrix/table/set
    newData : Constant
        A scalar/vector/tuple/table/set.

        - If obj is a vector, newData is a scalar, vector, or tuple whose elements
          are of the same type as obj. The result is a vector longer than obj.

        - If obj is a tuple, newData is a scalar, vector or tuple:

          - If newData is a vector, it is appended to obj as one tuple element;

          - If newData is a tuple, the appendTupleAsAWhole configuration parameter
            controls whether it is appended to obj as one tuple element (true) or
            each of its elements is appended independently (false).

        - If obj is a matrix, newData is a vector whose length must be a multiple of
          the number of rows of obj. The result is a matrix with the same number of
          rows as obj but with more columns.

        - If obj is a table, newData is a table with the same number of columns as obj.
          The result is a table with the same number and name of columns as obj but with more rows.

        - If newData and obj are of different data forms, `append_` will attempt to convert
          newData to the same data form as obj. If it is not possible, return an error message.
    """
    ...


@builtin_function(_appendTuple_)
def appendTuple_(X: Constant, Y: Constant, wholistic: Constant = DFLT) -> Constant:
    r"""Append Y to X.

    Parameters
    ----------
    X : Constant
        A tuple
    Y : Constant
        A tuple
    wholistic : Constant, optional
        A Boolean, by default DFLT
    """
    ...


@builtin_function(_array)
def array(dataType: Union[Alias[Literal["template"]], Constant], initialSize: Constant = DFLT, capacity: Constant = DFLT, defaultValue: Constant = DFLT) -> Constant:
    r"""Return a vector.

    Parameters
    ----------
    dataType : Union[Alias[Literal[&quot;template&quot;]], Constant]
        The data type for the vector.
    initialSize : Constant, optional
        An existing vector, by default DFLT. The existing vector serves as a template
        and its data type determines the new vector's data type.
    capacity : Constant, optional
        The initial size (in terms of the number of elements) of the vector, by default DFLT.
        When the number of elements exceeds capacity, the system will first allocate memory
        of 1.2~2 times of capacity, copy the data to the new memory space, and release
        the original memory.
    defaultValue : Constant, optional
        The default value of the vector, by default DFLT
    """
    ...


@builtin_function(_arrayVector)
def arrayVector(index: Constant, value: Constant) -> Constant:
    r"""Convert value into an array vector by spliting it based on the elements in index.

    Parameters
    ----------
    index : Constant
        A a vector of positive integers, which must be strictly monotonically increasing.
    value : Constant
        A ector.
    """
    ...


@builtin_function(_asFreq)
def asFreq(X: Constant, rule: Constant, closed: Constant = DFLT, label: Constant = DFLT, origin: Constant = DFLT, fill: Constant = DFLT, limit: Constant = DFLT) -> Constant:
    r"""Convert X to specified frequency.

    Parameters
    ----------
    X : Constant
        An indexed matrix or indexed series. The index must be of temporal type.
    rule : Constant
        A string that can take the following values:

        +---------------+----------------------------------+
        | Value of rule | Corresponding DolphinDB function |
        +===============+==================================+
        | B             | businessDay                      |
        +---------------+----------------------------------+
        | W             | weekEnd                          |
        +---------------+----------------------------------+
        | WOM           | weekOfMonth                      |
        +---------------+----------------------------------+
        | LWOM          | lastWeekOfMonth                  |
        +---------------+----------------------------------+
        | M             | monthEnd                         |
        +---------------+----------------------------------+
        | MS            | monthBegin                       |
        +---------------+----------------------------------+
        | BM            | businessMonthEnd                 |
        +---------------+----------------------------------+
        | BMS           | businessMonthBegin               |
        +---------------+----------------------------------+
        | SM            | semiMonthEnd                     |
        +---------------+----------------------------------+
        | SMS           | semiMonthBegin                   |
        +---------------+----------------------------------+
        | Q             | quarterEnd                       |
        +---------------+----------------------------------+
        | QS            | quarterBegin                     |
        +---------------+----------------------------------+
        | BQ            | businessQuarterEnd               |
        +---------------+----------------------------------+
        | BQS           | businessQuarterBegin             |
        +---------------+----------------------------------+
        | REQ           | FY5253Quarter                    |
        +---------------+----------------------------------+
        | A             | yearEnd                          |
        +---------------+----------------------------------+
        | AS            | yearBegin                        |
        +---------------+----------------------------------+
        | BA            | businessYearEnd                  |
        +---------------+----------------------------------+
        | BAS           | businessYearBegin                |
        +---------------+----------------------------------+
        | RE            | FY5253                           |
        +---------------+----------------------------------+
        | D             | date                             |
        +---------------+----------------------------------+
        | H             | hourOfDay                        |
        +---------------+----------------------------------+
        | min           | minuteOfHour                     |
        +---------------+----------------------------------+
        | S             | secondOfMinute                   |
        +---------------+----------------------------------+
        | L             | millisecond                      |
        +---------------+----------------------------------+
        | U             | microsecond                      |
        +---------------+----------------------------------+
        | N             | nanosecond                       |
        +---------------+----------------------------------+
        | SA            | semiannualEnd                    |
        +---------------+----------------------------------+
        | SAS           | semiannualBegin                  |
        +---------------+----------------------------------+


        The strings above can also be used with positive integers for parameter rule.
        For example, "2M" means the end of every two months. In addition, rule can also
        be set as the identifier of the trading calendar, e.g., the Market Identifier
        Code of an exchange, or a user-defined calendar name. Positive integers can
        also be used with identifiers. For example, "2XNYS" means every two trading
        days of New York Stock Exchange.

    closed : Constant, optional
        A string indicating which boundary of the interval is closed, by default DFLT.

        - The default value is 'left' for all values of rule except for 'M', 'A', 'Q',
          'BM', 'BA', 'BQ', and 'W' which all have a default of 'right'.

        - The default is 'right' if origin is 'end' or 'end_day'.
    label : Constant, optional
        A string indicating which boundary is used to label the interval, by default DFLT.

        - The default value is 'left' for all values of rule except for 'M', 'A', 'Q',
          'BM', 'BA', 'BQ', and 'W' which all have a default of 'right'.

        - The default is 'right' if origin is 'end' or 'end_day'.
    origin : Constant, optional
        A string or a scalar of the same data type as X indicating the timestamp
        where the intervals start, by default DFLT. It can be 'epoch', start', 'start_day',
        'end', 'end_day' or a user-defined time object. The default value is 'start_day'.

        - 'epoch': origin is 1970-01-01

        - 'start': origin is the first value of the timeseries

        - 'start_day': origin is 00:00 of the first day of the timeseries

        - 'end': origin is the last value of the timeseries

        - 'end_day': origin is 24:00 of the last day of the timeseries
    """
    ...


@builtin_function(_asin)
def asin(X: Constant) -> Constant:
    r"""The inverse sine (arcsine) function.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_asinh)
def asinh(X: Constant) -> Constant:
    r"""The inverse hyperbolic sine function.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_asis)
def asis(obj: Constant) -> Constant:
    r"""Return a reference of obj.

    Parameters
    ----------
    obj : Constant
        Can be of any data type.
    """
    ...


@builtin_function(_asof)
def asof(X: Constant, Y: Constant) -> Constant:
    r"""For each element y in Y, return the index of the last element in X that is no greater than y.

    Parameters
    ----------
    X : Constant
        A ector/indexed series/indexed matrix sorted in ascending order.
    Y : Constant
        A scalar/vector/tuple/matrix/dictionary/table/array vector.
    """
    ...


@builtin_function(_at)
def at(X: Constant, index: Constant = DFLT) -> Constant:
    r"""Retrieves elements or positions from a data structure based on specified indices,
    Boolean conditions, or ranges, and can also apply arguments to functions.

    Parameters
    ----------
    X : Constant
        If only one parameter is specified: X is a Boolean expression/vector or an integer vector.
        If both parameters are specified: X is a scalar/vector (including tuples and array vectors)
        /matrix/table/dictionary/pair/function.
    index : Constant, optional
        A Boolean expression/Boolean value/scalar/vector (including tuples and array vectors)
        /pair, by default DFLT
    """
    ...


@builtin_function(_atImax)
def atImax(location: Constant, value: Constant) -> Constant:
    r"""Find the position of the element with the largest value in location, and return
    the value of the element in the same position in value.

    Parameters
    ----------
    location : Constant
        vectors/matrices/tables of the same dimensions
    value : Constant
        vectors/matrices/tables of the same dimensions
    """
    ...


@builtin_function(_atImin)
def atImin(location: Constant, value: Constant) -> Constant:
    r"""Find the position of the element with the smallest value in location, and return
    the value of the element in the same position in value.

    Parameters
    ----------
    location : Constant
        vectors/matrices/tables of the same dimensions.
    value : Constant
        vectors/matrices/tables of the same dimensions.
    """
    ...


@builtin_function(_atan)
def atan(X: Constant) -> Constant:
    r"""The inverse tangent (arctan) function.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_atanh)
def atanh(X: Constant) -> Constant:
    r"""The inverse hyperbolic tangent function.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_autocorr)
def autocorr(X: Constant, lag: Constant) -> Constant:
    r"""Calculate the autocorrelation of X.

    Parameters
    ----------
    X : Constant
        A vector.
    lag : Constant
        A positive integer.
    """
    ...


@builtin_function(_avg)
def avg(X: Constant) -> Constant:
    r"""Calculate the average of X.

    - If X is a vector, calculate the average of X.

    - If X is a matrix, calculate the average of each column and return a vector.

    - If X is a table, calculate the average of each column and return a table.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix/table.
    """
    ...


@builtin_function(_backup)
def backup(backupDir: Constant, dbPath: Union[Alias[Literal["sqlObj"]], Constant], force: Constant = DFLT, parallel: Constant = DFLT, snapshot: Constant = DFLT, tableName: Constant = DFLT, partition: Constant = DFLT, keyPath: Constant = DFLT) -> Constant:
    r"""Back up all or specified partitions of a distributed table.

    Parameters
    ----------
    backupDir : Constant
        A string indicating the directory to save the backup. For an AWS S3 directory,
        it must begin with s3://.
    dbPath : Union[Alias[Literal[&quot;sqlObj&quot;]], Constant]
        A string indicating the database path. If specified, back up the database by
        copying partitions. If backupDir is an AWS S3 directory, only dbPath can be specified.
    force : Constant, optional
        A Boolean value, by default DFLT. True means to perform a full backup, otherwise
        to perform an incremental backup.
    parallel : Constant, optional
        A Boolean value indicating whether to back up partitions in parallel, by default DFLT.
    snapshot : Constant, optional
        A Boolean value indicating whether to synchronize the deletion of tables/partitions
        to the backup database, by default DFLT. It only takes effect when the parameter partition is empty.
    tableName : Constant, optional
        A STRING scalar or vector indicating the name of table to be backed up.
        If unspecified, all tables of the database are backed up, by default DFLT.
    partition : Constant, optional
        Indicates the partitions to be backed up. It can be:

        - a STRING scalar or vector indicating the path(s) to one or multiple partitions
          of a database, and each path starts with "/". Note that for a compo-partitioned
          database, the path must include all partition levels.

        - filter condition(s). A filter condition can be a scalar or vector where each
          element represents a partition.

          - For a single-level partitioning database, it is a scalar.

          - For a compo-partitioned database, it is a tuple composed of filter conditions
            with each element for a partition level. If a partition level has no filter
            condition, the corresponding element in the tuple is empty.

          - unspecified to indicate all partitions.
    keyPath : Constant, optional
        A STRING scalar that specifies the path to the TDE key file used for backup encryption, by default DFLT

    Returns
    -------
    Constant
        An integer indicating the number of partitions that have been backed up successfully.
    """
    ...


@builtin_function(_backupDB)
def backupDB(backupDir: Constant, dbPath: Constant, keyPath: Constant = DFLT) -> Constant:
    r"""Back up the specific database to the specified directory.

    Parameters
    ----------
    backupDir : Constant
        A string indicating the directory to save the backup.
    dbPath : Constant
        A string indicating the database path.
    keyPath : Constant, optional
        A  STRING scalar that specifies the path to the TDE key file used for backup
        encryption, by default DFLT
    """
    ...


@builtin_function(_backupSettings)
def backupSettings(fileName: Constant, userPermission: Constant = DFLT, functionView: Constant = DFLT) -> Constant:
    r"""Back up all settings on users, permissions, and function views to specified directory.

    Parameters
    ----------
    fileName : Constant
        A STRING scalar specifying the backup file path. It can be an absolute path
        or relative path to <HomeDir>.
    userPermission : Constant, optional
        A Boolean scalar indicating whether to back up user permissions, by default DFLT.
    functionView : Constant, optional
        A Boolean scalar indicating whether to back up function views, by default DFLT.

    Returns
    -------
    Constant
        A vector containing all backup user names and function views.
    """
    ...


@builtin_function(_backupTable)
def backupTable(backupDir: Constant, dbPath: Constant, tableName: Constant, keyPath: Constant = DFLT) -> Constant:
    r"""Back up a table to the specified directory.

    Parameters
    ----------
    backupDir : Constant
        A string indicating the directory to save the backup.
    dbPath : Constant
        A string indicating the database path.
    tableName : Constant
        A string indicating the table name.
    keyPath : Constant, optional
        A string that specifies the path to the TDE key file used for backup encryption,
        by default DFLT.
    """
    ...


@builtin_function(_bar)
def bar(X: Constant, interval: Constant, closed: Constant = DFLT) -> Constant:
    r"""bar can group X based on the length specified by interval.

    Parameters
    ----------
    X : Constant
        An integral/temporal scalar or vector.
    interval : Constant
        An integral/DURATION type scalar greater than 0 or a vector of the same length as X.
        When interval is of type DURATION, the following time units are supported
        (case-sensitive): w, d, H, m, s, ms, us, ns.

        .. note::

            As time units y and M are not supported in interval, to group X by year
            or month, convert the data format of X with function month or year. Specify
            the interval as an integer for calculation. You can refer to Example 2.

    closed : Constant, optional
        A string which can take 'left' (default) or 'right', indicating whether an
        element of X that is divisible by interval is the left boundary (the first element of the group)
        or the right boundary (the last element of the group) of a group, by default DFLT.

    Returns
    -------
    Constant
        A vector with the same length as X.
    """
    ...


@builtin_function(_base64Decode)
def base64Decode(X: Constant) -> Constant:
    r"""Decode X from Base64 format to binary data.

    Parameters
    ----------
    X : Constant
        A STRING scalar or vector.

    Returns
    -------
    Constant
        A BLOB scalar or vector.
    """
    ...


@builtin_function(_base64Encode)
def base64Encode(X: Constant) -> Constant:
    r"""Encode X to Base64 format.

    Parameters
    ----------
    X : Constant
        A STRING scalar or vector.

    Returns
    -------
    Constant
        A STRING scalar or vector.
    """
    ...


@builtin_function(_beta)
def beta(Y: Constant, X: Constant) -> Constant:
    r"""Return the coefficient estimate of an ordinary-least-squares regression of Y on X (with intercept).

    Parameters
    ----------
    Y : Constant
        A vector
    X : Constant
        A vector
    """
    ...


@builtin_function(_between)
def between(X: Constant, Y: Constant) -> Constant:
    r"""Check if each element of X is between the pair indicated by Y (both boundaries are inclusive).

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix.
    Y : Constant
        A pair indicating a range.
    """
    ...


@builtin_function(_bfill_)
def bfill_(obj: Constant, limit: Constant = DFLT) -> Constant:
    r"""- If obj is a vector: back fill the null values in obj with the next non-null value.
    - If obj is a matrix or a table: back fill the null values in each column of obj
    with the next non-null value.

    Parameters
    ----------
    obj : Constant
        A vector, matrix, or table.
    limit : Constant, optional
        A positive integer indicating the number of null values to be filled, by default DFLT
    """
    ...


@builtin_function(_bigarray)
def bigarray(dataType: Union[Alias[Literal["template"]], Constant], initialSize: Constant = DFLT, capacity: Constant = DFLT, defaultValue: Constant = DFLT) -> Constant:
    r"""Big arrays are specially designed for advanced users in big data analysis.
    Regular arrays use continuous memory. If there is not enough continuous memory,
    an out of memory exception will occur. A big array consists of many small memory
    blocks instead of one large block of memory. Therefore big arrays help relieve
    the memory fragmentation issue. This, however, may come with light performance
    penalty for certain operations.

    Parameters
    ----------
    dataType : Union[Alias[Literal[&quot;template&quot;]], Constant]
        The data type for the big array.
    initialSize : Constant, optional
        The initial size (in terms of the number of elements) of the big array, by default DFLT.
        If the first parameter is a data type, then initialSize is required; if the first
        parameter is an existing big array, then initialSize is optional.
    capacity : Constant, optional
        The amount of memory (in terms of the number of elements) allocated to the
        big array, by default DFLT.
        When the number of elements exceeds capacity, the system will first allocate
        memory of 1.2~2 times of capacity, copy the data to the new memory space,
        and release the original memory.
    defaultValue : Constant, optional
        The default value of the big array, by default DFLT.
        For many data types, the default values are 0. For string and symbol, the
        default values are null values.
    """
    ...


@builtin_function(_binaryExpr)
def binaryExpr(X: Constant, Y: Constant, optr: Constant) -> Constant:
    r"""Connect X and Y with the binary operator specified in optr to generate metacode
    of a binary expression.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix.
    Y : Constant
        A scalar or a vector of the same type as X.
    optr : Constant
        A binary operator.
    """
    ...


@builtin_function(_binsrch)
def binsrch(X: Constant, Y: Constant) -> Constant:
    r"""binsrch means binary search. For each element in Y, binsrch locates its position in X.
    If nothing is found, it returns -1(s).

    Parameters
    ----------
    X : Constant
        A vector sorted in ascending order.
    Y : Constant
        A scalar/vector/tuple/matrix/array vector/dictionary/table.
    """
    ...


@builtin_function(_bitAnd)
def bitAnd(X: Constant, Y: Constant) -> Constant:
    r"""Return the result of the bitAnd operation.

    Parameters
    ----------
    X : Constant
        A numeric scalar/vector/matrix/table.
    Y : Constant
        A numeric scalar/vector/matrix/table.
    """
    ...


@builtin_function(_bitOr)
def bitOr(X: Constant, Y: Constant) -> Constant:
    r"""Return the result of the bitOr operation.

    Parameters
    ----------
    X : Constant
        A numeric scalar/vector/matrix/table.
    Y : Constant
        A numeric scalar/vector/matrix/table.
    """
    ...


@builtin_function(_bitXor)
def bitXor(X: Constant, Y: Constant) -> Constant:
    r"""Return the result of the bitXOr operation.

    Parameters
    ----------
    X : Constant
        A numeric scalar/vector/matrix/table.
    Y : Constant
        A numeric scalar/vector/matrix/table.
    """
    ...


@builtin_function(_blob)
def blob(X: Constant) -> Constant:
    r"""Convert the data type of X to BLOB.

    Parameters
    ----------
    X : Constant
        A STRING scalar/vector.
    """
    ...


@builtin_function(_bondAccrInt)
def bondAccrInt(start: Constant, maturity: Constant, issuePrice: Constant, coupon: Constant, frequency: Constant, dayCountConvention: Constant, bondType: Constant, settlement: Constant, benchmark: Constant = DFLT) -> Constant:
    r"""Returns the accrued interest of a security.

    Parameters
    ----------
    start : Constant
        A calar or vector of DATE type indicating the bond’s value date.
    maturity : Constant
        A DATE scalar or vector indicating the maturity date.
    issuePrice : Constant
        A numeric scalar or vector of the same length as start indicating the bond’s
        issue price. For discount bonds, the actual issue price must be specified
        (typically less than 100); for other bonds, it is usually 100.
    coupon : Constant
        A numeric scalar or vector indicating the annual coupon rate. For example,
        0.03 indicates a 3% annual coupon.
    frequency : Constant
        An INT scalar/vector indicating the number of payments, or a STRING scalar/vector
        indicating payment frequency. It can be:

        - 0/"Once": Bullet payment at maturity.

        - 1/"Annual": Annual payments.

        - 2/"Semiannual": Semi-annual payments.

        - 4/"Quarterly": Quarterly payments.

        - 12/"Monthly": Monthly payments.
    dayCountConvention : Constant
        A STRING scalar or vector indicating the day count convention to use. It can be:

        - "Thirty360US": US (NASD) 30/360

        - "ActualActualISMA" (default): actual/actual (ISMA rule)

        - "Actual360": actual/360

        - "Actual365": actual/365

        - "Thirty360EU": European 30/360

        - "ActualActualISDA" (default): actual/actual (ISDA rule)
    bondType : Constant
        A STRING scalar or vector indicating the bond type. It can be:

        - "FixedRate": Fixed-rate bond, where interest is paid periodically based on the coupon rate.

        - "Discount": Discount bond, where no interest is paid, and the bond is
          issued at a discount. FV at maturity = face value.

        - "ZeroCoupon": Zero-coupon bond, where interest and face value are paid
          at maturity. FV at maturity = face value + interest.
    settlement : Constant
        A DATE scalar or vector indicating the settlement date.
    benchmark : Constant, optional
        A STRING scalar indicating the reference algorithm, by default DFLT.
        Currently, only "Excel" (the algorithm used in Excel) is supported.

    Returns
    -------
    Constant
        A scalar or vector of DOUBLE type.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_bondCashflow)
    def bondCashflow(start: Constant, maturity: Constant, coupon: Constant, frequency: Constant, dayCountConvention: Constant, bondType: Constant, mode: Constant = DFLT) -> Constant:
        r"""Calculates the cash flow for a bond with a face value of 100. Supports fixed-rate
        bonds, zero-coupon bonds, and discount bonds.

        Parameters
        ----------
        start : Constant
            A calar or vector of DATE type indicating the bond’s value date.
        maturity : Constant
            A DATE scalar or vector indicating the maturity date.
        coupon : Constant
            A numeric scalar or vector indicating the annual coupon rate. For example,
            0.03 indicates a 3% annual coupon.
        frequency : Constant
            An INT scalar/vector indicating the number of payments, or a STRING scalar/vector
            indicating payment frequency. It can be:

            - 0/"Once": Bullet payment at maturity.

            - 1/"Annual": Annual payments.

            - 2/"Semiannual": Semi-annual payments.

            - 4/"Quarterly": Quarterly payments.

            - 12/"Monthly": Monthly payments.
        dayCountConvention : Constant
            A STRING scalar or vector indicating the day count convention to use. It can be:

            - "Thirty360US": US (NASD) 30/360

            - "ActualActualISMA" (default): actual/actual (ISMA rule)

            - "Actual360": actual/360

            - "Actual365": actual/365

            - "Thirty360EU": European 30/360

            - "ActualActualISDA" (default): actual/actual (ISDA rule)
        bondType : Constant
            A STRING scalar or vector indicating the bond type. It can be:

            - "FixedRate": Fixed-rate bond, where interest is paid periodically based on the coupon rate.

            - "Discount": Discount bond, where no interest is paid, and the bond is issued
              at a discount. FV at maturity = face value.

            - "ZeroCoupon": Zero-coupon bond, where interest and face value are paid at maturity.
              FV at maturity = face value + interest.
        mode : Constant, optional
            A STRING scalar or vector specifying the output format, by default DFLT. The values are:

            - "Vector" (default): returns only the cash flow amounts.

            - "Table": returns a detailed cash flow table.

        Returns
        -------
        Constant
            - If mode = "Vector", it returns a DOUBLE vector or an array vector that lists
              the cash flow amounts for a single bond or multiple bonds.

            - If mode = "Table", it returns a table or a tuple of tables, each representing
              the detailed cash flows of a single bond or multiple bonds.
              Each table contains the following fields:

              - paymentDate: DATE, payment date.

              - coupon: DOUBLE, interest amount.

              - notional: DOUBLE, principal.

              - total: DOUBLE, total amount.
        """
        ...


if not sw_is_ce_edition():
    @builtin_function(_bondConvexity)
    def bondConvexity(start: Constant, maturity: Constant, issuePrice: Constant, coupon: Constant, frequency: Constant, dayCountConvention: Constant, bondType: Constant, settlement: Constant, price: Constant, priceType: Constant, benchmark: Constant = DFLT) -> Constant:
        r"""Returns the bond convexity of a bond with a face value of 100.

        Parameters
        ----------
        start : Constant
            A calar or vector of DATE type indicating the bond’s value date.
        maturity : Constant
            A DATE scalar or vector indicating the maturity date.
        issuePrice : Constant
            A numeric scalar or vector of the same length as start indicating the bond’s
            issue price. For discount bonds, the actual issue price must be specified
            (typically less than 100); for other bonds, it is usually 100.
        coupon : Constant
            A numeric scalar or vector indicating the annual coupon rate. For example,
            0.03 indicates a 3% annual coupon.
        frequency : Constant
            An INT scalar/vector indicating the number of payments, or a STRING scalar/vector
            indicating payment frequency. It can be:

            - 0/"Once": Bullet payment at maturity.

            - 1/"Annual": Annual payments.

            - 2/"Semiannual": Semi-annual payments.

            - 4/"Quarterly": Quarterly payments.

            - 12/"Monthly": Monthly payments.
        dayCountConvention : Constant
            A STRING scalar or vector indicating the day count convention to use. It can be:

            - "Thirty360US": US (NASD) 30/360

            - "ActualActualISMA" (default): actual/actual (ISMA rule)

            - "Actual360": actual/360

            - "Actual365": actual/365

            - "Thirty360EU": European 30/360

            - "ActualActualISDA" (default): actual/actual (ISDA rule)
        bondType : Constant
            A STRING scalar or vector indicating the bond type. It can be:

            - "FixedRate": Fixed-rate bond, where interest is paid periodically based on the coupon rate.

            - "Discount": Discount bond, where no interest is paid, and the bond is issued
              at a discount. FV at maturity = face value.

            - "ZeroCoupon": Zero-coupon bond, where interest and face value are paid
              at maturity. FV at maturity = face value + interest.
        settlement : Constant
            A DATE scalar or vector indicating the settlement date.
        price : Constant
            A numeric scalar or vector indicating the bond's yield to maturity.
        priceType : Constant
            A STRING scalar or vector used to specify the type of the bond price (price).
            Currently, only "YTM" (Yield to Maturity) is supported.
        benchmark : Constant, optional
            A STRING scalar indicating the reference algorithm, by default DFLT.
            Currently, only "Excel" (the algorithm used in Excel) is supported.

        Returns
        -------
        Constant
            A scalar or vector of type DOUBLE.
        """
        ...


if not sw_is_ce_edition():
    @builtin_function(_bondDirtyPrice)
    def bondDirtyPrice(start: Constant, maturity: Constant, issuePrice: Constant, coupon: Constant, frequency: Constant, dayCountConvention: Constant, bondType: Constant, settlement: Constant, price: Constant, priceType: Constant, benchmark: Constant = DFLT) -> Constant:
        r"""Returns the dirty price of a bond with a face value of 100.

        Parameters
        ----------
        start : Constant
            A calar or vector of DATE type indicating the bond’s value date.
        maturity : Constant
            A DATE scalar or vector indicating the maturity date.
        issuePrice : Constant
            A numeric scalar or vector of the same length as start indicating the bond’s issue price.
            For discount bonds, the actual issue price must be specified (typically less than 100);
            for other bonds, it is usually 100.
        coupon : Constant
            A numeric scalar or vector indicating the annual coupon rate. For example,
            0.03 indicates a 3% annual coupon.
        frequency : Constant
            An INT scalar/vector indicating the number of payments, or a STRING scalar/vector
            indicating payment frequency. It can be:

            - 0/"Once": Bullet payment at maturity.

            - 1/"Annual": Annual payments.

            - 2/"Semiannual": Semi-annual payments.

            - 4/"Quarterly": Quarterly payments.

            - 12/"Monthly": Monthly payments.
        dayCountConvention : Constant
            A STRING scalar or vector indicating the day count convention to use. It can be:

            - "Thirty360US": US (NASD) 30/360

            - "ActualActualISMA" (default): actual/actual (ISMA rule)

            - "Actual360": actual/360

            - "Actual365": actual/365

            - "Thirty360EU": European 30/360

            - "ActualActualISDA" (default): actual/actual (ISDA rule)
        bondType : Constant
            A STRING scalar or vector indicating the bond type. It can be:

            - "FixedRate": Fixed-rate bond, where interest is paid periodically based on the coupon rate.

            - "Discount": Discount bond, where no interest is paid, and the bond is issued
              at a discount. FV at maturity = face value.

            - "ZeroCoupon": Zero-coupon bond, where interest and face value are paid at maturity.
              FV at maturity = face value + interest.
        settlement : Constant
            A DATE scalar or vector indicating the settlement date.
        price : Constant
            A numeric scalar or vector whose meaning depends on the value of priceType:

            - When priceType is "YTM", price indicates the bond's yield to maturity.

            - When priceType is "CleanPrice", price indicates the bond's clean price.
        priceType : Constant
            A STRING scalar or vector used to specify the type of the bond price (price). It can be:

            - "YTM": Yield to Maturity.

            - "CleanPrice": Clean price.
        benchmark : Constant, optional
            A STRING scalar indicating the reference algorithm, by default DFLT. Currently,
            only "Excel" (the algorithm used in Excel) is supported.

        Returns
        -------
        Constant
            A scalar or vector of type DOUBLE.
        """
        ...


if not sw_is_ce_edition():
    @builtin_function(_bondDuration)
    def bondDuration(start: Constant, maturity: Constant, issuePrice: Constant, coupon: Constant, frequency: Constant, dayCountConvention: Constant, bondType: Constant, settlement: Constant, price: Constant, priceType: Constant, benchmark: Constant = DFLT) -> Constant:
        r"""Returns the Macaulay duration for an assumed par value of 100.

        Parameters
        ----------
        start : Constant
            A calar or vector of DATE type indicating the bond’s value date.
        maturity : Constant
            A DATE scalar or vector indicating the maturity date.
        issuePrice : Constant
            A numeric scalar or vector of the same length as start indicating the bond’s
            issue price. For discount bonds, the actual issue price must be specified
            (typically less than 100); for other bonds, it is usually 100.
        coupon : Constant
            A numeric scalar or vector indicating the annual coupon rate. For example,
            0.03 indicates a 3% annual coupon.
        frequency : Constant
            An INT scalar/vector indicating the number of payments, or a STRING scalar/vector
            indicating payment frequency. It can be:

            - 0/"Once": Bullet payment at maturity.

            - 1/"Annual": Annual payments.

            - 2/"Semiannual": Semi-annual payments.

            - 4/"Quarterly": Quarterly payments.

            - 12/"Monthly": Monthly payments.
        dayCountConvention : Constant
            A STRING scalar or vector indicating the day count convention to use. It can be:

            - "Thirty360US": US (NASD) 30/360

            - "ActualActualISMA" (default): actual/actual (ISMA rule)

            - "Actual360": actual/360

            - "Actual365": actual/365

            - "Thirty360EU": European 30/360

            - "ActualActualISDA" (default): actual/actual (ISDA rule)
        bondType : Constant
            A STRING scalar or vector indicating the bond type. It can be:

            - "FixedRate": Fixed-rate bond, where interest is paid periodically based on the coupon rate.

            - "Discount": Discount bond, where no interest is paid, and the bond is issued
              at a discount. FV at maturity = face value.

            - "ZeroCoupon": Zero-coupon bond, where interest and face value are paid at
              maturity. FV at maturity = face value + interest.
        settlement : Constant
            A DATE scalar or vector indicating the settlement date.
        price : Constant
            A numeric scalar or vector indicates the bond's yield to maturity.

        priceType : Constant
            A STRING scalar or vector used to specify the type of the bond price (price). Currently, only "YTM" is supported.

        benchmark : Constant, optional
            A STRING scalar indicating the reference algorithm, by default DFLT.
            Currently, only "Excel" (the algorithm used in Excel) is supported.


        Returns
        -------
        Constant
            A scalar or vector of type DOUBLE.
        """
        ...


if not sw_is_ce_edition():
    @builtin_function(_bondYield)
    def bondYield(start: Constant, maturity: Constant, issuePrice: Constant, coupon: Constant, frequency: Constant, dayCountConvention: Constant, bondType: Constant, settlement: Constant, price: Constant, priceType: Constant, method: Constant = DFLT, maxIter: Constant = DFLT, benchmark: Constant = DFLT) -> Constant:
        r"""Calculate the bond yield for each 100 face value of a bond based on its clean price or dirty price.

        Parameters
        ----------
        start : Constant
            A calar or vector of DATE type indicating the bond’s value date.
        maturity : Constant
            A DATE scalar or vector indicating the maturity date.
        issuePrice : Constant
            A numeric scalar or vector of the same length as start indicating the bond’s issue price.
            For discount bonds, the actual issue price must be specified (typically less than 100);
            for other bonds, it is usually 100.
        coupon : Constant
            A numeric scalar or vector indicating the annual coupon rate. For example,
            0.03 indicates a 3% annual coupon.
        frequency : Constant
            An INT scalar/vector indicating the number of payments, or a STRING scalar/vector
            indicating payment frequency. It can be:

            - 0/"Once": Bullet payment at maturity.

            - 1/"Annual": Annual payments.

            - 2/"Semiannual": Semi-annual payments.

            - 4/"Quarterly": Quarterly payments.

            - 12/"Monthly": Monthly payments.
        dayCountConvention : Constant
            A STRING scalar or vector indicating the day count convention to use. It can be:

            - "Thirty360US": US (NASD) 30/360

            - "ActualActualISMA" (default): actual/actual (ISMA rule)

            - "Actual360": actual/360

            - "Actual365": actual/365

            - "Thirty360EU": European 30/360

            - "ActualActualISDA" (default): actual/actual (ISDA rule)
        bondType : Constant
            A STRING scalar or vector indicating the bond type. It can be:

            - "FixedRate": Fixed-rate bond, where interest is paid periodically based on the coupon rate.

            - "Discount": Discount bond, where no interest is paid, and the bond is issued
              at a discount. FV at maturity = face value.

            - "ZeroCoupon": Zero-coupon bond, where interest and face value are paid at maturity.
              FV at maturity = face value + interest.
        settlement : Constant
            A DATE scalar or vector indicating the settlement date.
        price : Constant
            A numeric scalar or vector whose meaning depends on the value of priceType:

            - When priceType is "CleanPrice", price indicates the bond's clean price.

            - When priceType is "DirtyPrice", price indicates the bond's dirty price.
        priceType : Constant
            A STRING scalar or vector used to specify the type of the bond price (price). It can be:

            - "CleanPrice": Clean price.

            - "DirtyPrice": Dirty price.
        method : Constant, optional
            A STRING scalar or vector indicating the optimization algorithm used to solve the bond yield, by default DFLT. It can be:

            - "newton" (default): Newton algorithm.

            - "brent": Brent algorithm.

            - "nm": Nelder-Mead simplex algorithm.

            - "bfgs": BFGS algorithm.

            - "lbfgs": LBFGS algorithm.
        maxIter : Constant, optional
            A positive integer or a vector of positive integers indicating the maximum
            number of iterations, by default DFLT.
        benchmark : Constant, optional
            A STRING scalar indicating the reference algorithm, by default DFLT.
            Currently, only "Excel" (the algorithm used in Excel) is supported.

        Returns
        -------
        Constant
            A DOUBLE scalar or vector.
        """
        ...


@builtin_function(_bool)
def bool(X: Constant) -> Constant:
    r"""Convert the input to a Boolean value.

    Parameters
    ----------
    X : Constant
        Can be of any data type.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_brentq)
    def brentq(f: Constant, a: Constant, b: Constant, xtol: Constant = DFLT, rtol: Constant = DFLT, maxIter: Constant = DFLT, funcDataParam: Constant = DFLT) -> Constant:
        r"""Find a root x0 of a function f in a bracketing interval [a, b] using Brent's method.

        Parameters
        ----------
        f : Constant
            A function which returns a number. The function fmust be continuous in [a,b],
            and f(a) and f(b) must have opposite signs.
        a : Constant
            A numeric scalar that specifies the left boundary of the bracketing interval [a,b].
        b : Constant
            A numeric scalar that specifies the right boundary of the bracketing interval [a,b].
        xtol : Constant, optional
            A numeric scalar that specify the precision of the computed root, by default DFLT.
            The computed root x0 satisfies `|x-x0| <= (xtol + rtol* |x0|)`, where x is the exact root.
            The default value of xtol is 2e-12, and the default value of rtol is 4 times
            the machine epsilon in double precision.
        rtol : Constant, optional
            A numeric scalar that specify the precision of the computed root, by default DFLT.
            The computed root x0 satisfies `|x-x0| <= (xtol + rtol* |x0|)`, where x is the exact root.
            The default value of xtol is 2e-12, and the default value of rtol is 4 times
            the machine epsilon in double precision.
        maxIter : Constant, optional
            An integer indicating the maximum iterations, by default DFLT
        funcDataParam : Constant, optional
            A vector containing extra arguments for the function f, by default DFLT

        Returns
        -------
        Constant
            A vector res of length 2.
        """
        ...


if not sw_is_ce_edition():
    @builtin_function(_brute)
    def brute(func: Constant, ranges: Constant, ns: Constant = DFLT, finish: Constant = DFLT) -> Constant:
        r"""Minimize a function over a given range by brute force.

        Parameters
        ----------
        func : Constant
            The name of the function to be minimized. Note that its return value must be a numeric scalar.
        ranges : Constant
            A tuple of tuples Each tuple element can take the following forms:

            - (low, high): Specifies the minimum and maximum values for a parameter.

            - (low, high, num): Also includes the number of grid points between low and high.
        ns : Constant, optional
            A positive number indicating the number of grid points along the axes,
            by default DFLT. If ranges is specified as (low, high, num), num determines
            the number of points. Otherwise, ns is used, defaulting to 20 if not provided.
        finish : Constant, optional
            An optimization function that is called with the result of brute force
            minimization as initial guess, by default DFLT.  finish should be a function
            that returns a dictionary that contains keys 'xopt' and 'fopt' and their values
            should be numeric. The default value is the fmin function. If set to NULL,
            no "polishing" function is applied and the result of brute is returned directly.

        Returns
        -------
        Constant
            A dictionary with the following members:

            - xopt: Parameter that minimizes function.

            - fopt: Value of function at minimum: fopt = f(xopt).
        """
        ...


@builtin_function(_bucket)
def bucket(vector: Constant, dataRange: Constant, bucketNum: Constant, includeOutbound: Constant = DFLT) -> Constant:
    r"""Return a vector with the same length as the input vector. Each element of the
    result indicates which bucket each of the elements of the input vector belongs to,
    based on the bucket classification rules given by dataRange and bucketNum.

    Parameters
    ----------
    vector : Constant
        A numeric or temporal vector
    dataRange : Constant
        A pair indicating the data range, which includes the lower bound and excludes
        the upper bound.
    bucketNum : Constant
        The number of buckets. When dataRange is specified as an INT PAIR, its range
        must be a multiple of bucketNum.
    includeOutbound : Constant, optional
        A Boolean value indicating whether to include the bucket below the lower bound
        of the data range and the bucket beyond the upper bound of the data range, by default DFLT

    Returns
    -------
    Constant
        A vector with the same length as the input vector.
    """
    ...


@builtin_function(_bucketCount)
def bucketCount(vector: Constant, dataRange: Constant, bucketNum: Constant, includeOutbound: Constant = DFLT) -> Constant:
    r"""Accept the same set of parameters as the function bucket and return the count for each bucket.

    Parameters
    ----------
    vector : Constant
        A numeric or temporal vector
    dataRange : Constant
        A pair indicating the data range, which includes the lower bound and excludes
        the upper bound.
    bucketNum : Constant
        The number of buckets. When dataRange is specified as an INT PAIR, its range
        must be a multiple of bucketNum.
    includeOutbound : Constant, optional
        A Boolean value indicating whether to include the bucket below the lower bound
        of the data range and the bucket beyond the upper bound of the data range, by default DFLT.
    """
    ...


@builtin_function(_businessDay)
def businessDay(X: Constant, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""If X is a business day (Monday to Friday), return date(X). Otherwise, return
    the most recent business day.
    If parameter offset is specified, the result is updated every n business days.
    Parameter offset works only if parameter n>1.

    Parameters
    ----------
    X : Constant
        A scalar/vector of data type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    offset : Constant, optional
        A scalar of the same data type as X, by default DFLT. It must be no greater
        than the minimum value of X. The default value is the minimum value of X.
    n : Constant, optional
        A positive integer, by default DFLT
    """
    ...


@builtin_function(_businessMonthBegin)
def businessMonthBegin(X: Constant, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""Return the first business day (Monday to Friday) of the month that X belongs to.

    Parameters
    ----------
    X : Constant
        A scalar/vector of data type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    offset : Constant, optional
        A scalar of the same data type as X, by default DFLT. It must be no greater
        than the minimum value of X. The default value is the minimum value of X.
    n : Constant, optional
        A positive integer, by default DFLT
    """
    ...


@builtin_function(_businessMonthEnd)
def businessMonthEnd(X: Constant, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""Return the last business day (Monday to Friday) of the month that X belongs to.

    Parameters
    ----------
    X : Constant
        A scalar/vector of data type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    offset : Constant, optional
        A scalar of the same data type as X, by default DFLT. It must be no greater
        than the minimum value of X. The default value is the minimum value of X.
    n : Constant, optional
        A positive integer, by default DFLT
    """
    ...


@builtin_function(_businessQuarterBegin)
def businessQuarterBegin(X: Constant, startingMonth: Constant = DFLT, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""Return the first business day (Monday to Friday) of the quarter that X belongs to.

    Parameters
    ----------
    X : Constant
        A scalar/vector of data type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    startingMonth : Constant, optional
        An integer between 1 and 12 indicating a month, by default DFLT
    offset : Constant, optional
        A scalar of the same data type as X, by default DFLT. It must be no greater
        than the minimum value of X. The default value is the minimum value of X.
    n : Constant, optional
        A positive integer, by default DFLT
    """
    ...


@builtin_function(_businessQuarterEnd)
def businessQuarterEnd(X: Constant, endingMonth: Constant = DFLT, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""Return the last day of the quarter that X belongs to.

    Parameters
    ----------
    X : Constant
        A scalar/vector of data type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    endingMonth : Constant, optional
        An integer between 1 and 12 indicating a month, by default DFLT
    offset : Constant, optional
        A scalar of the same data type as X, by default DFLT. It must be no greater
        than the minimum value of X. The default value is the minimum value of X.
    n : Constant, optional
        A positive integer, by default DFLT
    """
    ...


@builtin_function(_businessYearBegin)
def businessYearBegin(X: Constant, startingMonth: Constant = DFLT, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""Return the first business day (Monday to Friday) of the year that X belongs to
    and that starts in the month of startingMonth.

    Parameters
    ----------
    X : Constant
        A scalar/vector of data type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    startingMonth : Constant, optional
        An integer between 1 and 12 indicating a month, by default DFLT.
    offset : Constant, optional
        A scalar of the same data type as X, by default DFLT. It must be no greater
        than the minimum value of X. The default value is the minimum value of X.
    n : Constant, optional
        A positive integer, by default DFLT
    """
    ...


@builtin_function(_businessYearEnd)
def businessYearEnd(X: Constant, endingMonth: Constant = DFLT, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""Return the last business day (Monday to Friday) of the year that X belongs to
    and that ends in the month of endingMonth.

    Parameters
    ----------
    X : Constant
        A scalar/vector of data type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    endingMonth : Constant, optional
        An integer between 1 and 12 indicating a month, by default DFLT.
    offset : Constant, optional
        A scalar of the same data type as X, by default DFLT. It must be no greater
        than the minimum value of X. The default value is the minimum value of X.
    n : Constant, optional
        A positive integer, by default DFLT.
    """
    ...


@builtin_function(_byColumn)
def byColumn(func: Constant, X: Constant, Y: Constant = DFLT) -> Constant:
    r"""If func is a unary function, apply the specified function to each column of X;
    if func is a binary function, apply func(Xi, Yi) to each column of X and Y.

    **Calculation rules:**

    - If X/Y is a matrix, table, or tuple, byColumn applies func to each column of X/Y.

    - If X/Y is an array vector or columnar tuple, byRow applies func to each row of
      the transpose of X/Y.

    - If func is a vector function, byColumn returns the transpose of the result.

    - If func is an aggregate function, byColumn directly returns a vector.
      Certain aggregate functions in DolphinDB are optimized to work natively by column,
      requiring no transpose of the input X/Y. These include: sum, sum2, avg, min, max,
      count, imax, imin, imaxLast, iminLast, prod, std, stdp, var, varp, skew, kurtosis,
      any, all, corr, covar, wavg, wsum, beta, euclidean, dot, tanimoto.

    Parameters
    ----------
    func : Constant
        A unary function.  When function with multiple parameters is specified for
        func, partial application is used to fix part of the parameters. It can be
        a vector function (where the input vector and output vector are of equal length)
        or an aggregate function.
    X : Constant
        A matrix/table/tuple/array vector/columnar tuple.
    Y : Constant, optional
        A matrix/table/tuple/array vector/columnar tuple, by default DFLT

    Returns
    -------
    Constant
        If func is an aggregate function:

        - If X/Y is a matrix, array vector, or columnar tuple, byColumn returns a
          vector of the same size as the number of columns in X/Y.

        - If X/Y is a tuple, byColumn returns a tuple.

        - If X/Y is a table, byColumn returns a table.

        If func is a vector function, byColumn returns a result with the same form
        and dimension as X/Y.
    """
    ...


@builtin_function(_byRow)
def byRow(func: Constant, X: Constant, Y: Constant = DFLT) -> Constant:
    r"""If func is a unary function, apply the specified function to each row of X;
    if func is a binary function, apply func(Xi, Yi) to each row of X and Y.

    Parameters
    ----------
    func : Constant
        Either a vector function (both input and output are vectors of equal length)
        or an aggregate function.
    X : Constant
        A matrix/table/tuple/array vector/columnar tuple.
    Y : Constant, optional
        A matrix/table/tuple/array vector/columnar tuple, by default DFLT

    Returns
    -------
    Constant
        If func is an aggregate function, byRow returns a vector of the same size as
        the number of rows in X/Y.
        If func is a vector function, byRow returns a result with the same form and
        dimension as X/Y.
    """
    ...


@builtin_function(_cacheDS_)
def cacheDS_(ds: Constant) -> Constant:
    r"""Instruct the system to cache the data source when it is executed next time.

    Parameters
    ----------
    ds : Constant
        A data source or a list of data sources.

    Returns
    -------
    Constant
        True or false to indicate if this operation is successful.
    """
    ...


@builtin_function(_cacheDSNow)
def cacheDSNow(ds: Constant) -> Constant:
    r"""Immediately execute and cache the data source.

    Parameters
    ----------
    ds : Constant
        A data source or a list of data sources.

    Returns
    -------
    Constant
        The total number of cached rows.
    """
    ...


@builtin_function(_call)
def call(func: Constant, *args) -> Constant:
    r"""Call a function with the specified parameters.

    Parameters
    ----------
    func : Constant
        A function.
    args : Constant
        The required parameters of func.
    """
    ...


@builtin_function(_cast)
def cast(obj: Constant, type: Constant) -> Constant:
    r"""Convert a data type to another; reshape a matrix, or convert between matrices and vectors.

    Parameters
    ----------
    X : Constant
        Can be of any data form.
    Y : Constant
        A data type or a data pair.
    """
    ...


@builtin_function(_cbrt)
def cbrt(X: Constant) -> Constant:
    r"""Return the square root of X.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix/table.
    """
    ...


@builtin_function(_cdfBeta)
def cdfBeta(alpha: Constant, beta: Constant, X: Constant) -> Constant:
    r"""Return the value of the cumulative distribution function of a beta distribution.

    Parameters
    ----------
    alpha : Constant
        A positive floating number.
    beta : Constant
        A positive floating number.
    X : Constant
        A numeric scalar or vector.
    """
    ...


@builtin_function(_cdfBinomial)
def cdfBinomial(trials: Constant, prob: Constant, X: Constant) -> Constant:
    r"""Return the value of the cumulative distribution function of a binomial distribution.

    Parameters
    ----------
    trials : Constant
        A positive integer.
    p : Constant
        A floating number between 0 and 1.
    X : Constant
        A numeric scalar and vector.
    """
    ...


@builtin_function(_cdfChiSquare)
def cdfChiSquare(df: Constant, X: Constant) -> Constant:
    r"""Return the value of the cumulative distribution function of a chi-squared distribution.

    Parameters
    ----------
    df : Constant
        A positive integer indicating the degree of freedom of a chi-squared distribution.
    X : Constant
        A numeric scalar or vector.
    """
    ...


@builtin_function(_cdfExp)
def cdfExp(mean: Constant, X: Constant) -> Constant:
    r"""Return the value of the cumulative distribution function of an exponential distribution.

    Parameters
    ----------
    mean : Constant
        The mean of an exponential distribution.
    X : Constant
        A numeric scalar or vector.
    """
    ...


@builtin_function(_cdfF)
def cdfF(numeratorDF: Constant, denominatorDF: Constant, X: Constant) -> Constant:
    r"""Return the value of the cumulative distribution function of an F distribution.

    Parameters
    ----------
    numeratorDF : Constant
        A positive integer indicating the degree of freedom of an F distribution.
    denominatorDF : Constant
        A positive integer indicating the degree of freedom of an F distribution.
    X : Constant
        A numeric scalar or vector.
    """
    ...


@builtin_function(_cdfGamma)
def cdfGamma(shape: Constant, scale: Constant, X: Constant) -> Constant:
    r"""Return the value of the cumulative distribution function of a gamma distribution.

    Parameters
    ----------
    shape : Constant
        A positive floating-point number.
    scale : Constant
        A positive floating-point number.
    X : Constant
        A numeric scalar or vector.
    """
    ...


@builtin_function(_cdfKolmogorov)
def cdfKolmogorov(X: Constant) -> Constant:
    r"""Return the value of the cumulative distribution function of a Kolmogorov distribution.

    Parameters
    ----------
    X : Constant
        A numeric scalar or vector.
    """
    ...


@builtin_function(_cdfLogistic)
def cdfLogistic(mean: Constant, s: Constant, X: Constant) -> Constant:
    r"""Return the value of the cumulative distribution function of a logistic distribution.

    Parameters
    ----------
    mean : Constant
        The mean of a logistic distribution.
    s : Constant
        The scale parameter of a logistic distribution.
    X : Constant
        A numeric scalar or vector.
    """
    ...


@builtin_function(_cdfNormal)
def cdfNormal(mean: Constant, stdev: Constant, X: Constant) -> Constant:
    r"""Return the value of the cumulative distribution function of a normal distribution.

    Parameters
    ----------
    mean : Constant
        The mean of a normal distribution.
    stdev : Constant
        The standard deviation of a normal distribution.
    X : Constant
        A numeric scalar or vector.
    """
    ...


@builtin_function(_cdfPoisson)
def cdfPoisson(mean: Constant, X: Constant) -> Constant:
    r"""Return the value of the cumulative distribution function of a Poisson distribution.

    Parameters
    ----------
    mean : Constant
        The mean of a Poisson distribution.
    X : Constant
        A numeric scalar or vector.
    """
    ...


@builtin_function(_cdfStudent)
def cdfStudent(df: Constant, X: Constant) -> Constant:
    r"""Return the value of the cumulative distribution function of a Student's t-distribution.

    Parameters
    ----------
    df : Constant
        A positive floating number indicating the degree of freedom of a Student's t-distribution.
    X : Constant
        A numeric scalar or vector.
    """
    ...


@builtin_function(_cdfUniform)
def cdfUniform(lower: Constant, upper: Constant, X: Constant) -> Constant:
    r"""Return the value of the cumulative distribution function of a continuous uniform distribution.

    Parameters
    ----------
    lower : Constant
        A numeric scalar indicating the lower bound of a continuous uniform distribution.
    upper : Constant
        A numeric scalar indicating the upper bound of a continuous uniform distribution.
    X : Constant
        A numeric scalar or vector.
    """
    ...


@builtin_function(_cdfWeibull)
def cdfWeibull(alpha: Constant, beta: Constant, X: Constant) -> Constant:
    r"""Return the value of the cumulative distribution function of a Weibull distribution.

    Parameters
    ----------
    alpha : Constant
        A positive floating number.
    beta : Constant
        A positive floating number.
    X : Constant
        A numeric scalar or vector.
    """
    ...


@builtin_function(_cdfZipf)
def cdfZipf(num: Constant, exponent: Constant, X: Constant) -> Constant:
    r"""Return the value of the cumulative distribution function of a Zipfian distribution.

    Parameters
    ----------
    num : Constant
        A positive integer.
    exponent : Constant
        A non-negative floating number.
    X : Constant
        A numeric scalar or vector.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_cds)
    def cds(settlement: Constant, maturity: Constant, evalDate: Constant, notional: Constant, spread: Constant, riskFree: Constant, recovery: Constant, isSeller: Constant, frequency: Constant, calendar: Constant, convention: Constant = DFLT, termDateConvention: Constant = DFLT, rule: Constant = DFLT, basis: Constant = DFLT) -> Constant:
        r"""Value a Credit Default Swap (CDS) contract.

        Parameters
        ----------
        settlement : Constant
            A DATE scalar or vector indicating the settlement date.
        maturity : Constant
            A DATE scalar or vector indicating the maturity date.
        evalDate : Constant
            A DATE scalar or vector indicating the evaluation date of the CDS contract. Note that evalDate should be no later than settlement.
        notional : Constant
            A non-negative numeric scalar or vector indicating the notional principal of the CDS contract.
        spread : Constant
            A numeric scalar or vector indicating the CDS spread.
        riskFree : Constant
            A numeric scalar or vector indicating the risk-free interest rate.
        recovery : Constant
            A numeric scalar or vector in [0,1), indicating the recovery rate.
        isSeller : Constant
            A BOOLEAN scalar or vector indicating whether the party is the buyer or the seller.
        frequency : Constant
            An INT scalar/vector indicating the number of payments, or a STRING scalar/vector
            indicating payment frequency. It can be:

            - 0/"Once": Bullet payment at maturity.

            - 1/"Annual": Annual payments.

            - 2/"Semiannual": Semi-annual payments.

            - 4/"Quarterly": Quarterly payments.

            - 12/"Monthly": Monthly payments.
        calendar : Constant
            A STRING scalar or vector indicating the trading calendar(s).
        convention : Constant, optional
            A STRING scalar or vector indicating how cash flows that fall on a non-trading
            day are treated. The following options are available. Defaults to 'Following'.

            - 'Following': The following trading day.

            - 'ModifiedFollowing': The following trading day. If that day is in a different month, the preceding trading day is adopted instead.

            - 'Preceding': The preceding trading day.

            - 'ModifiedPreceding': The preceding trading day. If that day is in a different month, the following trading day is adopted instead.

            - 'Unadjusted': Unadjusted.

            - 'HalfMonthModifiedFollowing': The following trading day. If that day crosses the mid-month (15th) or the end of month, the preceding trading day is adopted instead.

            - 'Nearest': The nearest trading day. If both the preceding and following trading days are equally far away, default to following trading day.
        termDateConvention : Constant, optional
            A STRING scalar or vector indicating how maturity date that falls on a non-trading day is treated. Parameter options and the default value are the same as convention.
        rule : Constant, optional
            A STRING scalar or vector indicating how the list of dates is generated. It can be:

            - 'Backward': Backward from maturity date to settlement date.

            - 'Forward': Forward from settlement date to maturity date.

            - 'Zero': No intermediate dates between settlement date and maturity date.

            - 'ThirdWednesday': All dates but settlement date and maturity date are taken to be on the third Wednesday of their month (with forward calculation).

            - 'ThirdWednesdayInclusive': All dates are taken to be on the third Wednesday of their month (with forward calculation).

            - 'Twentieth': All dates but the settlement date are taken to be the twentieth of their month (used for CDS schedules in emerging markets). The maturity date is also modified.

            - 'TwentiethIMM': All dates but the settlement date are taken to be the twentieth of an IMM (International Money Market) month(used for CDS schedules). The maturity date is also modified.

            - 'OldCDS': Same as TwentiethIMM with unrestricted date ends and long/short stub coupon period (old CDS convention).

            - 'CDS' (default): Credit derivatives standard rule defined in the "Big Bang" Protocol in 2009.

            - 'CDS2015': Ammended credit derivatives standard rule that took effect on December 20, 2015.
        Returns
        -------
        Constant
            A DOUBLE scalar or vector.
        """
        ...


@builtin_function(_ceil)
def ceil(X: Constant) -> Constant:
    r"""Functions floor and ceil map a real number to the largest previous and the smallest following integer, respectively. Function round maps a real number to the largest previous or the smallest following integer with the round half up rule.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix.
    """
    ...


@builtin_function(_cell)
def cell(obj: Constant, row: Constant, col: Constant) -> Constant:
    r"""Return a scalar that is the value of the specified cell: obj[row, col]. The cell function runs generally faster than obj[row, col].

    Parameters
    ----------
    obj : Constant
        A matrix or table.
    row : Constant
        A non-negative integer indicating a column number.
    col : Constant
        A non-negative integer indicating a row number.
    """
    ...


@builtin_function(_cells)
def cells(obj: Constant, row: Constant, col: Constant) -> Constant:
    r"""Return a vector of cells in a matrix by the specified row and column index.

    Parameters
    ----------
    obj : Constant
        A matrix.
    row : Constant
        A vector of integral type, indicating indices of rows.
    col : Constant
        A vector of integral type of the same length as row, indicating indices of columns.
    """
    ...


@builtin_function(_char)
def char(X: Constant) -> Constant:
    r"""Convert the input to the data type of CHAR.

    Parameters
    ----------
    X : Constant
        Can be of any data type.
    """
    ...


@builtin_function(_charAt)
def charAt(X: Constant, Y: Constant) -> Constant:
    r"""Return the character in X at the position specified by Y.

    Parameters
    ----------
    X : Constant
        A STRING scalar/vector.
    Y : Constant
        An integer scalar/vector. If Y is a vector, it must be of the same length as X.

    Returns
    -------
    Constant
        A scalar/vector of data type CHAR.
    """
    ...


@builtin_function(_checkBackup)
def checkBackup(backupDir: Constant, dbPath: Constant, tableName: Constant = DFLT, partition: Constant = DFLT) -> Constant:
    r"""Check the data integrity of the backup files.

    Parameters
    ----------
    backupDir : Constant
        A string indicating the directory to save the backup.
    dbPath : Constant
        A string indicating the database path.
    tableName : Constant, optional
        A string indicating the table name. If tableName is unspecified, all tables in the database are checked.
    partition : Constant, optional
        A string indicating the relative path of the backup partitions. Use "?" as a
        single wildcard and "%" as a wildcard that can match zero or more characters.

        - For a certain partition, specify the relative path or "%/" + "partition name".

        - For all the partitions: specify "%".

    Returns
    -------
    Constant
        An empty table if all backup files are complete and accurate; otherwise return the information of abnormal backup files. You can set force=true for function backup to enable force backup to restore the corrupt backup partitions.
    """
    ...


@builtin_function(_chiSquareTest)
def chiSquareTest(X: Constant, Y: Constant = DFLT) -> Constant:
    r"""If X is a vector, conduct a Chi-squared goodness of fit test whether X and Y follow the same distribution. If X is a matrix/table, conduct Pearson's Chi-squared test on X.

    Parameters
    ----------
    X : Constant
        A numeric vector/matrix/table. If X is a vector, Y is a numeric vector of the same length as X. Y is not required if X is not a vector.

    Returns
    -------
    Constant
        A dictionary with the following keys:

        - pValue: p-value of the test

        - df: degree of freedom

        - chiSquaredValue: Chi-squared test statistic

        - method: either "Chi-square goodness of fit test" or "Pearson's Chi-squared test"
    """
    ...


@builtin_function(_cholesky)
def cholesky(obj: Constant, lower: Constant = DFLT) -> Constant:
    r"""Conduct Cholesky decomposition of a symmetric positive-definite matrix.

    Parameters
    ----------
    obj : Constant
        A symmetric positive definite matrix.
    lower : Constant, optional
        A Boolean value indicating whether the result is a lower triangular matrix (true, default) or an upper triangular matrix (false).
    """
    ...


@builtin_function(_cj)
def cj(leftTable: Constant, rightTable: Constant) -> Constant:
    r"""Perform a cross join between two tables and returns their Cartesian product. If X has n rows and Y has m rows, then cj(X,Y) has n*m rows.

    Parameters
    ----------
    X : Constant
        A table.
    Y : Constant
        A table.
    """
    ...


@builtin_function(_clear_)
def clear_(obj: Constant) -> Constant:
    r"""Clear the contents of X. After execution X still exists. It retains its initial data type and can be appended with new data.

    Parameters
    ----------
    X : Constant
        A vector, matrix, set, dictionary, or in-memory table.
    """
    ...


@builtin_function(_clearAllCache)
def clearAllCache() -> Constant:
    r"""Clear the following cached data:
        the data of dimension table stored in memory
        the data of OLAP DFS tables that has been loaded into memory
        the cached level file index of TSDB engine
        the cached SYMBOL base of TSDB engine
        the intermediate results of the map-reduce tasks in distributed computing
    """
    ...


@builtin_function(_clearAllIOTDBLatestKeyCache)
def clearAllIOTDBLatestKeyCache() -> Constant:
    r"""Clear the latest value table cache.
    """
    ...


@builtin_function(_clearAllIOTDBStaticTableCache)
def clearAllIOTDBStaticTableCache() -> Constant:
    r"""Clear the static table cache.
    """
    ...


@builtin_function(_clearAllTSDBSymbolBaseCache)
def clearAllTSDBSymbolBaseCache() -> Constant:
    r"""Clear all cached SYMBOL base entries that are absent from both the cache engine and ongoing transactions.
    """
    ...


@builtin_function(_clearDSCache_)
def clearDSCache_(ds: Constant) -> Constant:
    r"""Instruct the system to clear the cache after the next time the data source is executed.

    Parameters
    ----------
    ds : Constant
        A data source or a list of data sources.
    """
    ...


@builtin_function(_clearDSCacheNow)
def clearDSCacheNow(ds: Constant) -> Constant:
    r"""Immediately clear the data source and cache.

    Parameters
    ----------
    ds : Constant
        A data source or a list of data sources.
    """
    ...


@builtin_function(_clip)
def clip(X: Constant, Y: Constant, Z: Constant) -> Constant:
    r"""Clips X to specified range.

    Parameters
    ----------
    X : Constant
        A numeric or temporal scalar/vector/matrix/table, or a dictionary with numeric or temporal values.
    Y : Constant
        A numeric or temporal scalar/vector/matrix/table indicating the lower bound for the clipping range.
    Z : Constant
        A numeric or temporal scalar/vector/matrix/table indicating the upper bound for the clipping range.


    Returns
    -------
    Constant
        X' of the same data type and form as X.

        The following rules determine how X is clipped (If X is a dictionary, "element"
        indicates the dictionary value):

        - When Y and Z are scalars, the clipping range is [Y, Z]. Values outside this
          range are clipped to the nearest boundary.

          - Null Y or Z indicates no limit on the lower or upper bound.

          - If Y is greater than Z, all elements in X'areZ.

        - When Y and Z are vectors, matrices, or tables, each elementXi is clipped
          within the range [Yi, Zi]. Note: If any element in Y or Z is null, the
          corresponding element in X' is also null.

        - When Y or Z is a scalar, and the other is a vector, matrix, or table, each
          element Xi is clipped within the range [Y,Zi] or [Yi,Z].

          - The scalar represents a fixed boundary for all elements in X, while vector/
            matrix/table specify the boundary limits for Xi in the corresponding position.

          - If the scalar is null, no limit is set on the boundary. If any element in
            the vector, matrix or table is null, the corresponding element in X' is also null.

          - If Y is greater than Z for a specific position, the corresponding element in
            X' is set to Z.

        If X is a matrix or table, the aforementioned calculations will be performed on each column.
    """
    ...


@builtin_function(_clip_)
def clip_(X: Constant, Y: Constant, Z: Constant) -> Constant:
    r"""Clips X to specified range. The exclamation mark (_) means in-place change in DolphinDB.
    """
    ...


@builtin_function(_coalesce)
def coalesce(X1: Constant, X2: Constant, *args) -> Constant:
    r"""The function fills null values in X1 and returns a scalar or vector of the same dimension as X1.

    For each element in X1,

    - If not null, return the element;

    - If null, check the element at the same position in X2:

      - If not null, fill the null value in X1 with it;

      - If null, conduct the aforementioned calculation on the subsequent args until a non-null element is returned; Otherwise return NULL.

    Usage:

    - Merge multiple columns of a table into one column;

    - An alternative to complex case expression. For example, `select coalesce (expr1, expr2, 1) from t` is equivalent to `select case when vol1 is not null then vol1 when vol2 is not null then vol2 else 1 end from t`.

    Parameters
    ----------
    X1 : Constant
        A scalar or vector.
    X2 : Constant
        A scalar or vector of the same data type as X1. If X1 is a scalar, X2 must be a scalar; If X1 is a vector, X2 can be a non-null scalar or a vector of the same length as X1.
    args : Constant, optional
        Can be one or more arguments taking the same data type/form as X2.

    Returns
    -------
    Constant
        For each element in X1,

        - If not null, return the element;

        - If null, check the element at the same position in X2:

          - If not null, fill the null value in X1 with it;

          - If null, conduct the aforementioned calculation on the subsequent args until a non-null element is returned; otherwise return NULL.
    """
    ...


@builtin_function(_coevent)
def coevent(event: Constant, eventTime: Constant, window: Constant, orderSensitive: Constant = DFLT) -> Constant:
    r"""Count the number of occurrences of two events within the specified intervals.

    Parameters
    ----------
    event : Constant
        A vector indicating events.
    eventTime : Constant
        A temporal or integer vector of the same length as event indicating the timestamps of events.
    window : Constant
        A non-negative integer indicating the length of an interval.
    orderSensitive : Constant, optional
        A Boolean value indicating whether the order of the two events matters. The default value is false.

    Returns
    -------
    Constant
        A table with 3 columns: event1, event2 and hits. The values of event1 and event2 are based on the column event. Column hits is the number of occurrences of the event pair.
    """
    ...


@builtin_function(_coint)
def coint(Y0: Constant, Y1: Constant, trend: Constant = DFLT, method: Constant = DFLT, maxLag: Constant = DFLT, autoLag: Constant = DFLT) -> Constant:
    r"""Test for no-cointegration of a univariate equation.

    Parameters
    ----------
    Y0 : Constant
        A numeric vector indicating the first element in cointegrated system. Null values are not supported.
    Y1 : Constant
        A numeric vector or matrix indicating the remaining elements in cointegrated system. The number of elements in Y1 and Y0 must be equal. Null values are not supported.
    trend : Constant
        A scalar specifying the trend term included in regression for cointegrating
        equation. It can be

        - "c" : constant.

        - "ct" : constant and linear trend.

        - "ctt" : constant, and linear and quadratic trend.

        - "n" : no constant, no trend.
    method : Constant
        A string indicating the method for cointegration testing. Only "aeg" (augmented Engle-Granger) is available.
    maxLag : Constant
        A non-negative integer indicating the largest number of lags, which is used as an argument for adfuller.
    autoLag : Constant
        A string indicating the lag selection criterion, which is used as an argument
        for adfuller. It can be:

        - "aic": The number of lags is chosen to minimize the Akaike information criterion.

        - "bic": The number of lags is chosen to minimize the Bayesian information criterion.

        - "tstat": Start with maxLag and drops a lag until the t-statistic on the last
          lag length is significant using a 5%-sized test.

        - "max": The number of included lags is set to maxLag.

    Returns
    -------
    Constant
        A dictionary containing the following keys:

        - tStat: A floating-point scalar indicating the t-statistic of unit-root test on residuals.

        - pValue: A floating-point scalar indicating the MacKinnon's approximate p-value based on MacKinnon (1994, 2010).

        - criticalValues: A dictionary containing the critical values for the test statistic at the 1 %, 5 %, and 10 % levels based on regression curve.
    """
    ...


@builtin_function(_col)
def col(obj: Constant, index: Constant) -> Constant:
    r"""Return one or more columns of a vector/matrix/table.

    Parameters
    ----------
    obj : Constant
        A vector/matrix/table.
    index : Constant
        An integral scalar or pair.
    """
    ...


@builtin_function(_cols)
def cols(obj: Constant) -> Constant:
    r"""Return the total number of columns in X.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    """
    ...


@builtin_function(_columnNames)
def columnNames(obj: Constant) -> Constant:
    r"""Return the column names of X as a vector.

    Parameters
    ----------
    X : Constant
        A matrix/table.
    """
    ...


@builtin_function(_complex)
def complex(X: Constant, Y: Constant) -> Constant:
    r"""Create a complex number X+Y*i. The length of a complex number is 16 bytes. The low 8 bytes are stored in X, and the high 8 bytes are stored in Y.

    Parameters
    ----------
    X : Constant
        A  numeric scalar, pair, vector or matrix, which can be of Integral (excluding compress and INT128) or Floating type.
    Y : Constant
        A  numeric scalar, pair, vector or matrix, which can be of Integral (excluding compress and INT128) or Floating type.
    """
    ...


@builtin_function(_compress)
def compress(X: Constant, method: Constant = DFLT) -> Constant:
    r"""Compress a vector or a table with the specified compression algorithm. The compressed variable needs to be decompressed with function decompress before it can be used in a calculation.

    Parameters
    ----------
    X : Constant
        A vector or a table.
    method : Constant, optional
        A string indicating the compression algorithm. The available options are:

        - "lz4" (by default) is suitable for almost all data types. Although the "lz4"
          method may not achieve the highest compression ratio, it provides fast
          compression and decompression speeds.

        - "delta" option applies delta-of-delta algorithm, which is particularly
          suitable for data types like SHORT, INT, LONG, and date/time data.

        - "zstd" is also suitable for almost all data types. It provides a higher
          compression ratio compared to "lz4", but the compression and decompression
          speed is about half as fast as "lz4".

        - "chimp" is suitable for DOUBLE type data with decimal parts not exceeding
          three digits in length.
    """
    ...


@builtin_function(_concat)
def concat(str1: Union[Alias[Literal["X"]], Constant], str2: Union[Alias[Literal["separator"]], Constant]) -> Constant:
    r"""If X is a STRING/CHAR scalar

    - For an empty X,

      - if Y is an empty STRING/CHAR scalar, the function returns an empty string.

      - if Y is a non-empty STRING/CHAR scalar, the function returns Y.

    - Otherwise, the function forms a new string by combining X and Y regardless of
      whether Y is an empty string or not.

    - If X is a STRING/CHAR vector

      - For an empty X, the function returns an empty string.

      - Otherwise,

        - if Y is an empty STRING/CHAR scalar, the function concatenates each element
          in X and returns a string object;

        - if Y is a non-empty STRING/CHAR scalar, Y serves as the separator between
          the elements in vector X and the function returns a string object.

    .. note::

        The function concat implicitly converts all arguments to STRING type (null values to empty strings) before concatenation.

    Parameters
    ----------
    X : Constant
        A STRING/CHAR scalar or vector.
    Y : Constant
        A STRING/CHAR scalar. If X or Y is not specified, it is treated as an empty string.

    Returns
    -------
    Constant
        A STRING scalar.
    """
    ...


@builtin_function(_concatDateTime)
def concatDateTime(date: Constant, time: Constant) -> Constant:
    r"""Combine date and time into one new variable.

    Parameters
    ----------
    date : Constant
        A scalar/vector of data type DATE.
    time : Constant
        A scalar/vector of data type SECOND, TIME or NANOTIME. If date and time are
        both vectors, they must have the same length.

    Returns
    -------
    Constant
        If time is SECOND, return DATETIME.

        If time is TIME, return TIMESTAMP.

        If time is NANOTIME, return NANOTIMESTAMP.
    """
    ...


@builtin_function(_concatMatrix)
def concatMatrix(X: Constant, horizontal: Constant = DFLT) -> Constant:
    r"""Concatenate the matrices vertically or horizontally. When you concatenate matrices horizontally, they must have the same number of rows. When you concatenate them vertically, they must have the same number of columns.

    Parameters
    ----------
    X : Constant
        A tuple of multiple matrices.
    horizontal : Constant, optional
        A Boolean value indicating whether the matrices are contatenated horizontally. The default value is true. If set to false, the matrices are contatenated vertically.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_condValueAtRisk)
    def condValueAtRisk(returns: Constant, method: Constant, confidenceLevel: Constant = DFLT) -> Constant:
        r"""Calculate Conditional Value at Risk (CVaR), or expected shortfall (ES) to estimate the average losses incurred beyond the VaR level.

        Parameters
        ----------
        returns : Constant
            A numeric vector representing the returns. The element must be greater than -1 and cannot be empty.
        method : Constant
            A string indicating the CVaR calculation method, which can be:

            - 'normal': parametric method with normal distribution

            - 'logNormal': parametric method with log-normal distribution

            - 'historical': historical method

            - 'monteCarlo': Monte Carlo simulation
        confidenceLevel : Constant, optional
            A numeric scalar representing the confidence level, with a valid range of (0,1). The default value is 0.95.

        Returns
        -------
        Constant
            A DOUBLE value indicating the absolute value of the average losses that exceed the VaR. The value of VaR is returned if there is no return beyond the level.
        """
        ...


@builtin_function(_conditionalFilter)
def conditionalFilter(X: Constant, condition: Constant, filterMap: Constant) -> Constant:
    r"""Return true if both of the following conditions are satisfied, otherwise return false.

    - An element in the vector condition is a key to the dictionary filterMap;

    - The corresponding element in X is one of the elements of the key's value in the dictionary filterMap.

    If both X and condition are vectors, the result is a vector of the same length as X.

    Parameters
    ----------
    X : Constant
        A scalar/vector.
    condition : Constant
        A scalar or a vector of the same length as X.
    filterMap : Constant
        A dictionary indicating the filtering conditions.
    """
    ...


@builtin_function(_conditionalIterate)
def conditionalIterate(cond: Constant, trueValue: Constant, falseIterFunc: Constant) -> Constant:
    r"""Supposing the iteration is based only on the previous result, for the k-th (k ∈ N+) record, the calculation logic is (where the column "factor" holds the results):

    - cond[k] == true: factor[k] = trueValue

    - cond[k] == false: factor[k] = falseIterFunc(factor)[k-1]

    .. note::

        If falseIterFunc is a window function, the iteration is based on multiple previous results.

    Parameters
    ----------
    cond : Constant
        A conditional expression or a function with BOOLEAN return values. It must contain fields from the input table. Constants/constant expressions are not supported.
    trueValue : Constant
        The calculation formula.
    falseIterFunc : Constant
        The function for iteration, whose only parameter is the column from the output table. Currently, only the following functions are supported (use partial application to specify functions with multiple parameters):

        - Moving functions: tmove, tmavg, tmmax, tmmin, tmsum, mavg, mmax, mmin, mcount, msum;

        - Cumulative window functions: cumlastNot, cumfirstNot;

        - Order-sensitive functions: ffill, move.

        If cond returns true, the calculation of trueValue is triggered. If cond returns false, falseIterFunc is called for iteration.
    """
    ...


@builtin_function(_constantDesc)
def constantDesc(obj: Constant) -> Constant:
    r"""This function provides a description of an object.

    Parameters
    ----------
    obj : Constant
        An object.

    Returns
    -------
    Constant
        A dictionary with the following keys:

        - form : the data form

        - vectorType : the specific vector type, returns only when obj is a vector

        - isIndexedMatrix	: whether it is an indexed matrix, returns only when obj is a matrix

        - isIndexedSeries	: whether it is an indexed series, returns only when obj is a matrix

        - nullFlag : whether it contains null values, returns only when obj is a vector, pair, or matrix

        - isView : whether it is a view, returns only when obj is a vector, pair, or matrix

        - tableType : the specific table type, returns only when obj is a table

        - type : the data type

        - codeType : the specific metacode type, returns only when obj is metacode

        - functionDefType : the specific function type, returns only when obj is a function

        - scale : the number of decimal places, returns only when obj is of DECIMAL type

        - isColumnarTuple : whether it is a columnar tuple, returns only when obj is a tuple, excluding any view representations

        - category : the data type category

        - isTemporary : whether it is a temporary object

        - isIndependent : whether it is an independent object

        - isReadonly : whether it is a read-only object

        - isReadonlyArgument : whether it is a read-only argument

        - isStatic : whether it is a static object

        - isTransient : whether it is a transient object

        - copyOnWrite : whether it employs copy-on-write behavior

        - refCount : the count that has been referenced

        - address : the hexadecimal address

        - rows : the row count

        - columns : the column count

        - memoryAllocated : the memory allocated
    """
    ...


@builtin_function(_contextCount)
def contextCount(X: Constant, Y: Constant) -> Constant:
    r"""Count the number of positions that are not null in both X and Y.

    Parameters
    ----------
    X : Constant
        A vector.
    Y : Constant
        A vector.
        X and Y are of the same length.
    """
    ...


@builtin_function(_contextSum)
def contextSum(X: Constant, Y: Constant) -> Constant:
    r"""Get of positions that are not null in both X and Y, and calculate the sum of the elements in X on these positions.

    Parameters
    ----------
    X : Constant
        A vector, matrix or table.
    Y : Constant
        A vector, matrix or table.
    """
    ...


@builtin_function(_contextSum2)
def contextSum2(X: Constant, Y: Constant) -> Constant:
    r"""Get of positions that are not null in both X and Y, and calculate the sum of squares of the elements in X on these positions.

    Parameters
    ----------
    X : Constant
        A vector, matrix or table.
    Y : Constant
        A vector, matrix or table.

    Returns
    -------
    Constant
        A DOUBLE type (regardless of the data types of X and Y).
    """
    ...


@builtin_function(_contextby)
def contextby(func: Constant, funcArgs: Constant, groupingCol: Constant, sortingCol: Constant = DFLT, semanticFilter: Constant = DFLT, asc: Constant = DFLT, nullsOrder: Constant = DFLT) -> Constant:
    r"""Calculate func(funcArgs) for each groupingCol group.

    Parameters
    ----------
    func : Constant
        A function. For the second use case, func can only have one parameter (funcArg).
    funcArgs : Constant
        The parameters of func. It is a tuple if there are more than 1 parameter of func.
    groupingCol : Constant
        The grouping variable(s). It can be one or multiple vectors.
    sortingCol : Constant
        An optional argument for within group sorting before applying func.
    semanticFilter : Constant, optional
        A positive integer indicating which columns to include in calculations when funcArgs is a table. The possible values are:

        - 0 - All columns

        - 1 (default) - Columns of FLOATING, INTEGRAL, and DECIMAL categories, excluding the COMPRESSED data type.

        - 2 - Columns of TEMPORAL category.

        - 3 - Columns of LITERAL category, excluding the BLOB data type.

        - 4 - Columns of FLOATING, INTEGRAL, DECIMAL, and TEMPORAL categories, excluding the COMPRESSED data type.
    The vectors in groupingCol, sortingCol and each of the function argument in funcArgs all have the same size.

    Returns
    -------
    Constant
        A vector of the same size as each of the input arguments other than func. If func is an aggregate function, all elements within the same group have identical result. We can use sortingCol to sort the within-group data before the calculation.

        .. note::

            The keyword defg must be used to declare an aggregate function.
    """
    ...


@builtin_function(_convertEncode)
def convertEncode(str: Constant, srcEncode: Constant, destEncode: Constant) -> Constant:
    r"""Change the encoding of strings. All encoding names must use lowercase. The Linux version supports conversion between any two encodings. The Windows version only supports conversion between GBK and UTF-8.

    Parameters
    ----------
    str : Constant
        A STRING scalar/vector, a dictionary with string values, or a table.
    srcEncode : Constant
        A string indicating the original encoding name.
    destEncode : Constant
        A string indicating the new encoding name.
    """
    ...


@builtin_function(_convertExcelFormula)
def convertExcelFormula(formula: Constant, colStart: Constant, colEnd: Constant, rowStart: Constant, rowEnd: Constant) -> Constant:
    r"""Convert Excel formula to DolphinDB expressions.

    Parameters
    ----------
    formula : Constant
        A STRING scalar/vector indicating an Excel formula.
    colStart : Constant
        A STRING scalar indicating the starting column of the data in Excel.
    colEnd : Constant
        A STRING scalar indicating the ending column of the data in Excel.
    rowStart : Constant
        A positive integer indicating the starting row of the data in Excel.
    rowEnd : Constant
        A positive integer indicating the ending row of the data in Excel. rowEnd must be greater than or equal to rowStart.
    """
    ...


@builtin_function(_convertTZ)
def convertTZ(obj: Constant, srcTZ: Constant, destTZ: Constant) -> Constant:
    r"""Convert obj from time zone srcTZ to time zone destTZ. Daylight saving time is considered in time zone conversion.

    Parameters
    ----------
    obj : Constant
        A scalar or vector of DATETIME, TIMESTAMP, or NANOTIMESTAMP type.
    srcTZ : Constant
        A string indicating the time zone.
    destTZ : Constant
        A string indicating the time zone.
    """
    ...


@builtin_function(_copy)
def copy(obj: Constant) -> Constant:
    r"""Returns a shallow copy of obj. A shallow copy only copies the outer structure, while inner elements (sub-objects) still share references with the original object.

    Parameters
    ----------
    obj : Constant
        Can be of any data type.
    """
    ...


@builtin_function(_corr)
def corr(X: Constant, Y: Constant) -> Constant:
    r"""Calculate the correlation of X and Y. Note that when the variance of X or Y is 0, the return value is NULL.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    Y : Constant
        A vector/matrix/table.
        X and Y are of the same size. If X is a table, only the numeric and Boolean values are calculated.
    """
    ...


@builtin_function(_corrMatrix)
def corrMatrix(X: Constant) -> Constant:
    r"""Return a correlation matrix, where the (i, j) entry is the correlation between the columns i and j of X.

    Parameters
    ----------
    X : Constant
        A matrix.
    """
    ...


@builtin_function(_cos)
def cos(X: Constant) -> Constant:
    r"""Apply the function of cos to X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix.
    """
    ...


@builtin_function(_cosh)
def cosh(X: Constant) -> Constant:
    r"""The hyperbolic cosine function.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix.
    """
    ...


@builtin_function(_count)
def count(obj: Constant) -> Constant:
    r"""size returns the number of elements in a vector or matrix, while count returns the number of non-null elements in a vector/matrix. count can be used in a SQL query, but size cannot. For tables, size and count both return the number of rows.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_countNanInf)
def countNanInf(X: Constant, includeNull: Constant = DFLT) -> Constant:
    r"""An aggregate function that counts the number of NaN values and Inf values in X. When includeNull = true, the result includes the number of null values.

    Parameters
    ----------
    X : Constant
        A DOUBLE type scalar, vector or matrix.
    includeNull : Constant, optional
        A BOOLEAN value. The default value is false.
    """
    ...


@builtin_function(_covar)
def covar(X: Constant, Y: Constant) -> Constant:
    r"""Calculate the covariance of X and Y.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    Y : Constant, optional
        A vector/matrix/table.
        X and Y are of the same size. If X is a table, only the numeric and Boolean columns are calculated.
    """
    ...


@builtin_function(_covarMatrix)
def covarMatrix(X: Constant) -> Constant:
    r"""Return a covariance matrix, where the (i, j) entry is the covariance between the columns i and j of X.

    Parameters
    ----------
    X : Constant
        A matrix.
    """
    ...


@builtin_function(_crc32)
def crc32(str: Constant, cksum: Constant = DFLT) -> Constant:
    r"""Create a CRC32 hash from STRING. The result is of data type INT.

    Parameters
    ----------
    str : Constant
        A STRING scalar/vector.
    cksum : Constant, optional
        A integral scalar/vector. The default value is 0.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_crmwCBond)
    def crmwCBond(settlement: Constant, maturity: Constant, fv: Constant, ys: Constant, yd: Constant) -> Constant:
        ...


@builtin_function(_cross)
def cross(func: Constant, X: Constant, Y: Constant = DFLT) -> Constant:
    r"""Apply func to the permutation of all individual elements of X and Y and return a matrix.

    Parameters
    ----------
    func : Constant
        A binary function.
    X : Constant
        A pair/vector/matrix.
    Y : Constant, optional
        A pair/vector/matrix.
    X and Y can have different data forms and sizes. If Y is not specified, perform cross(func, X, X) where func must be a symmetric binary function, such as corr.
    """
    ...


@builtin_function(_crossStat)
def crossStat(X: Constant, Y: Constant) -> Constant:
    r"""Return a tuple with the following elements: count(X), sum(X), sum(Y), sum2(X), sum2(Y), sum(X*Y).

    Parameters
    ----------
    X : Constant
        A numeric vector.
    Y : Constant, optional
        A numeric vector.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_cubicSpline)
    def cubicSpline(X: Constant, Y: Constant, bc_type: Constant = DFLT) -> Constant:
        r"""Cubic spline data interpolator.

        Parameters
        ----------
        x : Constant
            A numeric vector containing values of the independent variable. The length of x must be no smaller than 3. Its values must be real and in strictly increasing order.
        y : Constant
            A numeric vector containing values of the dependent variable. The length of y must match the length of x.
        bc_type : Constant
            A STRING scalar, pair, or a vector of length no greater than 2. It specifies the boundary condition type.

            - If bc_type is a string or a vector of length 1, the specified condition will be applied at both ends of a spline.

            - If bc_type is a pair or a vector of length 2, the first and the second value will be applied at the curve start and end respectively.

            Its value can be:

            - "not-a-knot" (default): The first and second segment at a curve end are the same polynomial.

            - "clamped": The first derivative at curves ends are zero.

            - "natural": The second derivative at curve ends are zero.

        Returns
        -------
        Constant
            A dictionary withthe following keys:

            - c: Coefficients of the polynomials on each segment.

            - x: Breakpoints. The input x.

            - predict: A prediction function of the model, which returns the cubic spline interpolation result at point X. It can be called using model.predict(X) or predict(model, X), where

              - model: A dictionary indicating the output of cubicSpline.

              - X: A numeric vector indicating the X-coordinate of the point to be queried.

            - modelName: A string indicating the model name, which is “cubicSpline”.
        """
        ...


if not sw_is_ce_edition():
    @builtin_function(_cubicSplinePredict)
    def cubicSplinePredict(model: Constant, X: Constant) -> Constant:
        r"""Predict the corresponding y for x with the given model.

        Parameters
        ----------
        model : Constant
            A dictionary with two keys, c and x.
        x : Constant
            A numeric scalar or vector containing the independent variable to be predicted.
        """
        ...


@builtin_function(_cumPositiveStreak)
def cumPositiveStreak(X: Constant) -> Constant:
    r"""Cumulatively calculate the sum of consecutive positive elements of X after the last non-positive element to the left.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    """
    ...


@builtin_function(_cumavg)
def cumavg(X: Constant) -> Constant:
    r"""Calculate the cumulative average of X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    """
    ...


@builtin_function(_cumbeta)
def cumbeta(Y: Constant, X: Constant) -> Constant:
    r"""Cumulatively calculate the coefficient estimate of the regression of Y on X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    Y : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.

    Returns
    -------
    Constant
        A vector of the same length as X.
    """
    ...


@builtin_function(_cumcorr)
def cumcorr(X: Constant, Y: Constant) -> Constant:
    r"""Cumulatively calculate the correlation of X and Y.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    Y : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.

    Returns
    -------
    Constant
        A vector of the same length as X.
    """
    ...


@builtin_function(_cumcount)
def cumcount(X: Constant) -> Constant:
    r"""Cumulatively calculate the number of non-null elements in X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    """
    ...


@builtin_function(_cumcovar)
def cumcovar(X: Constant, Y: Constant) -> Constant:
    r"""Cumulatively calculate the covariance of X and Y.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    Y : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.

    Returns
    -------
    Constant
        A vector of the same length as X.
    """
    ...


@builtin_function(_cumfirstNot)
def cumfirstNot(X: Constant, k: Constant = DFLT) -> Constant:
    r"""If X is a vector:

    - If k is unspecified, return the first non-null element in X;

    - If k is specified, return the first element that is not k.

    If X is a matrix, conduct the aforementioned calculation within each column of X. The result is a matrix with the same shape as X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    k : Constant
        A scalar.
    """
    ...


@builtin_function(_cumlastNot)
def cumlastNot(X: Constant, k: Constant = DFLT) -> Constant:
    r"""If X is a vector:

    - If k is unspecified, return the last non-null element in X;

    - If k is specified, return the last element that is not k.

    If X is a matrix, conduct the aforementioned calculation within each column of X. The result is a matrix with the same shape as X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    k : Constant
        A scalar.
    """
    ...


@builtin_function(_cummax)
def cummax(X: Constant) -> Constant:
    r"""Cumulatively calculate the maximum values in X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_cummdd)
    def cummdd(X: Constant, ratio: Constant = DFLT) -> Constant:
        r"""Cumulatively calculate the maximum drawdown for the input X. Null values are ignored in calculation.

        Parameters
        ----------
        X : Constant
            A numeric vector, indicating the input data for calculating maximum drawdown (MDD), commonly cumulative return (or rate).
        ratio : Constant, optional
            A Boolean scalar indicating whether to express the MDD in ratio or absolute value.

            - true (default): Return the ratio of MDD over the peak.

            .. math::

                \begin{align*}
                \frac{\max_{t\in(0,T)} X_t - X_T}{\max_{t\in(0,T)} X_t}
                \end{align*}

            - false: Return the absolute value of MDD.

            .. math::
                \begin{align*}
                \max_{t\in(0,T)} X_t - X_T
                \end{align*}
        """
        ...


@builtin_function(_cummed)
def cummed(X: Constant) -> Constant:
    r"""Calculate the cumulative median of X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    """
    ...


@builtin_function(_cummin)
def cummin(X: Constant) -> Constant:
    r"""Cumulatively calculate the minimum values in X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    """
    ...


@builtin_function(_cumnunique)
def cumnunique(X: Constant, ignoreNull: Constant = DFLT) -> Constant:
    r"""Return the cumulative count of unique elements in X. Null values are included in the calculation.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    ignoreNull : Constant, optional
        A Boolean value. If set to true, only non-null elements will be included in the calculation. The default value is false.
    """
    ...


@builtin_function(_cumpercentile)
def cumpercentile(X: Constant, percent: Constant, interpolation: Constant = DFLT) -> Constant:
    r"""If X is a vector, cumulatively calculate the given percentile of a vector. The calculation ignores null values.

    If X is a matrix, conduct the aforementioned calculation within each column of X. The result is a matrix with the same shape as X.

    Parameters
    ----------
    X : Constant
        A vector or matrix.
    percent : Constant
        An integer or a floating point number between 0 and 100.
    interpolation : Constant, optional
        A string indicating the interpolation method to use if the specified percentile is between two elements in X (assuming the i-th and (i+1)-th element in the sorted X) . It can take the following values:

        - 'linear': Return X(i)+(X(t+1)-X(t))*fraction, where fraction = ((percentile100)-(i(size-1)))(1(size-1))

        - 'lower': Return X(i)

        - 'higher': Return X(i+1)

        - 'nearest': Return X(i) or X(i+1) that is closest to the specified percentile

        - 'midpoint': Return (X(i)+X(i+1))2

        The default value of interpolation is 'linear'.
    """
    ...


@builtin_function(_cumprod)
def cumprod(X: Constant) -> Constant:
    r"""Cumulatively calculate the product of the elements in X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    """
    ...


@builtin_function(_cumrank)
def cumrank(X: Constant, ascending: Constant = DFLT, ignoreNA: Constant = DFLT, tiesMethod: Constant = DFLT, percent: Constant = DFLT) -> Constant:
    r"""If X is a vector, for each element in X, return the position ranking from the first element to the current element. The result is of the same length as X. If ignoreNA = true, null values return NULL.

    If X is a matrix, conduct the aforementioned calculation within each column of X. The result is a matrix with the same shape as X.

    Parameters
    ----------
    X : Constant
        A vector/ matrix.
    ascending : Constant, optional
        A Boolean value indicating whether to sort in ascending order. The default value is true.
    ignoreNA : Constant, optional
        A Boolean value indicating whether null values are ignored in ranking. The default value is true.
    tiesMethod : Constant, optional
        A string indicating how to rank the group of records with the same value (i.e., ties):

        - 'min': lowest rank of the group

        - 'max': highest rank of the group

        - 'average': average rank of the group

    percent : Constant, optional
        A Boolean value, indicating whether to display the returned rankings in percentile form. The default value is false.
    """
    ...


@builtin_function(_cumstd)
def cumstd(X: Constant) -> Constant:
    r"""Cumulatively calculate the standard deviation of X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    """
    ...


@builtin_function(_cumstdp)
def cumstdp(X: Constant) -> Constant:
    r"""Cumulatively calculate the population standard deviation of X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    """
    ...


@builtin_function(_cumsum)
def cumsum(X: Constant) -> Constant:
    r"""Cumulatively calculate the sum of the elements in X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    """
    ...


@builtin_function(_cumsum2)
def cumsum2(X: Constant) -> Constant:
    r"""Cumulatively calculate the sum of squares of the elements in X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    """
    ...


@builtin_function(_cumsum3)
def cumsum3(X: Constant) -> Constant:
    r"""Cumulatively calculate the cubes of squares of the elements in X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    """
    ...


@builtin_function(_cumsum4)
def cumsum4(X: Constant) -> Constant:
    r"""Cumulatively calculate the fourth powers of the elements in X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    """
    ...


@builtin_function(_cumvar)
def cumvar(X: Constant) -> Constant:
    r"""Cumulatively calculate the variance of X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    """
    ...


@builtin_function(_cumvarp)
def cumvarp(X: Constant) -> Constant:
    r"""Cumulatively calculate the population variance of X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    """
    ...


@builtin_function(_cumwavg)
def cumwavg(X: Constant, Y: Constant) -> Constant:
    r"""Calculate the cumulative weighted average of X with Y as the weights.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    Y : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.

    Returns
    -------
    Constant
        A vector of the same length as X. Null values are ignored in the calculation.
    """
    ...


@builtin_function(_cumwsum)
def cumwsum(X: Constant, Y: Constant) -> Constant:
    r"""Calculate the cumulative weighted sum of X with Y as the weights.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    Y : Constant
        A scalar/vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.

    Returns
    -------
    Constant
        A vector of the same length as X. Null values are ignored in the calculation.
    """
    ...


@builtin_function(_cut)
def cut(X: Constant, size: Union[Alias[Literal["cutPositions"]], Constant]) -> Constant:
    r"""This function divides X based on the specified size or cutPositions.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    size : Constant
        A positive integer that must be no greater than the size of X.
    cutPositions : Constant
        A vector with increasing elements, which is used to specify the starting position of each vector in the result.

    Returns
    -------
    Constant
        A tuple.
    """
    ...


@builtin_function(_cutPoints)
def cutPoints(X: Constant, binNum: Constant, freq: Constant = DFLT) -> Constant:
    r"""Return a vector with (binNum+1) elements such that the elements of X are evenly distributed within each of the binNum buckets indicated by the vector. Each bucket is defined by two adjacent elements of the vector. The lower bound is inclusive and the upper bound is exclusive.

    Parameters
    ----------
    X : Constant
        A vector.
    binNum : Constant
        The number of buckets to be formed.
    freq : Constant, optional
        A vector with the same size as X. It specifies the frequency for each element in X. If it is specified, all the elements in X must be unique and sorted in ascending order.
    """
    ...


@builtin_function(_dailyAlignedBar)
def dailyAlignedBar(X: Constant, timeOffset: Constant, n: Constant, timeEnd: Constant = DFLT, mergeSessionEnd: Constant = DFLT) -> Constant:
    r"""Determine windows based on the starting time (specified by timeOffset),
    window length (specified by n), and possibly ending time (specified by timeEnd).
    For each element of X, return the starting time of the window it belongs to.
    Specifically, return X-((X-timeOffset)%n) for each element of X and return a
    vector with the same length as X.

    Parameters
    ----------
    X : Constant
        A temporal vector of type SECOND, TIME, NANOTIME, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    timeOffset : Constant
        A scalar/vector of type SECOND, TIME or NANOTIME with the same accuracy
        of X indicating the left boundary of session(s). If it is a vector, it
        must be increasing.
    n : Constant
        A positive integer or DURATION type data indicating the window length.
        If n is a positive integer, its unit is the minimum accuracy of timeOffset.
        If n is a DURATION type data, its unit cannot be y, M, w, d, B.
    timeEnd : Constant, optional
        Is of the same type and length of timeOffset indicating the right
        boundary of session(s).
    mergeSessionEnd : Constant, optional
        A Boolean value. When the right boundary of a session (as specified in
        timeEnd) is also the right boundary of a window, if mergeSessionEnd=true,
        the right boundary of the session is merged into the previous window.
    """
    ...


@builtin_function(_date)
def date(X: Constant) -> Constant:
    r"""Convert X into DATE type.

    Parameters
    ----------
    X : Constant
        An integer or temporal scalar/vector.
    """
    ...


@builtin_function(_datehour)
def datehour(X: Constant) -> Constant:
    r"""Convert X into DATEHOUR data type.

    Parameters
    ----------
    X : Constant
        A temporal scalar/vector that contains information about dates.
    """
    ...


@builtin_function(_datetime)
def datetime(X: Constant) -> Constant:
    r"""Convert X into DATETIME type.

    Parameters
    ----------
    X : Constant
        A temporal scalar/vector, or an integer.
    """
    ...


@builtin_function(_dayOfMonth)
def dayOfMonth(X: Constant) -> Constant:
    r"""Return the day of the month for each element in X.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type DATE, DATETIME, TIMESTAMP or NANOTIMESTAMP.

    Returns
    -------
    Constant
        An integer.
    """
    ...


@builtin_function(_dayOfWeek)
def dayOfWeek(X: Constant) -> Constant:
    r"""Return which day of the week is X.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type DATE, DATETIME, DATEHOUR, TIMESTAMP or NANOTIMESTAMP.

    Returns
    -------
    Constant
        An integer from 0 to 6, where 0 means Monday, .., 6 means Sunday.
    """
    ...


@builtin_function(_dayOfYear)
def dayOfYear(X: Constant) -> Constant:
    r"""Return the day of the year for each element in X.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type DATE, DATETIME, TIMESTAMP or NANOTIMESTAMP.

    Returns
    -------
    Constant
        An integer.
    """
    ...


@builtin_function(_daysInMonth)
def daysInMonth(X: Constant) -> Constant:
    r"""Return the number of days in the month for each element in X.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.

    Returns
    -------
    Constant
        An integer.
    """
    ...


@builtin_function(_decimal128)
def decimal128(X: Constant, scale: Constant) -> Constant:
    r"""Convert the input values into DECIMAL128.

    Parameters
    ----------
    X : Constant
        A scalar/vector of Integral, Floating, or STRING type.
    scale : Constant
        An integer in [0,38] that determines the number of digits to the right
        of the decimal point.
    """
    ...


@builtin_function(_decimal32)
def decimal32(X: Constant, scale: Constant) -> Constant:
    r"""Convert the input values into DECIMAL32 type.

    Parameters
    ----------
    X : Constant
        A scalar/vector of Integral, Floating, or STRING type.
    scale : Constant
        An integer in [0,9] that determines the number of digits to the right
        of the decimal point.
    """
    ...


@builtin_function(_decimal64)
def decimal64(X: Constant, scale: Constant) -> Constant:
    r"""Convert the input values into DECIMAL64.

    Parameters
    ----------
    X : Constant
        A scalar/vector of Integral, Floating, or STRING type.
    scale : Constant
        An integer in [0,18] that determines the number of digits to the right
        of the decimal point.
    """
    ...


@builtin_function(_decimalFormat)
def decimalFormat(X: Constant, format: Constant) -> Constant:
    r"""Apply a specified format to the given object.

    Parameters
    ----------
    X : Constant
        A scalar/vector of Integral or Floating type.
    format : Constant
        A string indicating the format to apply to X.

    Returns
    -------
    Constant
        A STRING scalar/vector.
    """
    ...


@builtin_function(_decimalMultiply)
def decimalMultiply(X: Constant, Y: Constant, scale: Constant) -> Constant:
    r"""The function multiplies Decimals. Compared with the mul function or operator `*`,
    the function can set the decimal places of the result with scale.

    .. note::

        In the following situations, the specified scale does not take effect and the
        function is equivalent to operator `*`.

        - Only one argument is of DECIMAL type (with scale S), and the specified scale
          is not equal to S.

        - X and Y are both of DECIMAL type (with scale S1 and S2, respectively), and the
          specified scale is smaller than min(S1, S2) or greater than (S1+S2).

        - One argument is a floating-point number.

    For the first two situations, the function return a DECIMAL type result, and
    for the third situation it returns a result of DOUBLE type.

    Parameters
    ----------
    X : Constant
        A scalar or vector, and at least one argument is of DECIMAL type.
    Y : Constant
        A scalar or vector, and at least one argument is of DECIMAL type.
    scale : Constant
        A non-negative integer indicating the decimal places to be retained in the result.
    """
    ...


@builtin_function(_decodeShortGenomeSeq)
def decodeShortGenomeSeq(X: Constant) -> Constant:
    r"""Decode the DNA sequences which have been encoded with encodeShortGenomeSeg.

    Parameters
    ----------
    X : Constant
        An integral scalar/vector.

    Returns
    -------
    Constant
        A STRING scalar or vector.
    """
    ...


@builtin_function(_decompress)
def decompress(X: Constant) -> Constant:
    r"""Decompress a compressed vector or a table.

    Parameters
    ----------
    X : Constant
        A compressed vector or a table.
    """
    ...


@builtin_function(_deepCopy)
def deepCopy(obj: Constant) -> Constant:
    r"""Returns a deep copy of obj. A deep copy copies all mutable elements,
    resulting in a fully independent replica of the original object.

    Parameters
    ----------
    obj : Constant
        Can be of any data type.
    """
    ...


@builtin_function(_defined)
def defined(names: Constant, type: Constant = DFLT) -> Constant:
    r"""Return a scalar/vector indicating whether each element of names is defined.

    Parameters
    ----------
    names : Constant
        A STRING scalar/vector indicating object name(s).
    type : Constant, optional
        Can be VAR (variable, default), SHARED (shared variable) or DEF
        (function definitions).
    """
    ...


@builtin_function(_defs)
def defs(pattern: Constant = DFLT) -> Constant:
    r"""If X is not specified, return all functions in the system as a table.

    If X is specified, return all functions with names consistent with the pattern of X.

    Parameters
    ----------
    X : Constant
        A string. It supports wildcard symbols "%" and "?". "%" means 0, 1 or
        multiple characters and "?" means 1 character.
    """
    ...


@builtin_function(_deg2rad)
def deg2rad(X: Constant) -> Constant:
    r"""Convert angle units from degrees to radians for each element of X.

    Parameters
    ----------
    X : Constant
        A scalar/vector.
    """
    ...


@builtin_function(_deltas)
def deltas(X: Constant, n: Constant = DFLT) -> Constant:
    r"""For each element Xi in X, return Xi-Xi-n, representing the differences between elements.

    Parameters
    ----------
    X : Constant
        A vector, matrix or table.
    n : Constant, optional
        An integer specifying the step to shift when comparing elements in X.
        The default value is 1, meaning to compare the current element with the
        adjacent element at left.

    Returns
    -------
    Constant
        A vector/matrix/table with the same shape as X.
    """
    ...


@builtin_function(_dema)
def dema(X: Constant, window: Constant) -> Constant:
    r"""Calculate the Double Exponential Moving Average (dema) for X in a sliding window
    of the given length.

    The formula is:

    ema1 = ema(x,window)

    dema = 2 * ema1 - ema(ema1,window)

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    window : Constant
        A positive integer indicating the size of the sliding window.
    """
    ...


@builtin_function(_demean)
def demean(X: Constant) -> Constant:
    r"""Center a dataset (zero-centering), and return an object of DOUBLE type
    with the same dimension as X. Null values are ignored in the calculation.

    - If X is a vector, calculate X - avg(X);

    - If X is a matrix, perform calculations by columns;

    - If X is a table, perform calculations only for numeric columns.

    Parameters
    ----------
    X : Constant
        A numeric scalar/vector/matrix/table.
    """
    ...


@builtin_function(_denseRank)
def denseRank(X: Constant, ascending: Constant = DFLT, ignoreNA: Constant = DFLT, percent: Constant = DFLT) -> Constant:
    r"""If X is a vector:

    - return the consecutive rank of each element in X based on the specified ascending order.

    - If ignoreNA = true, the null values are ignored in ranking and return NULL.

    If X is a matrix, conduct the aforementioned calculation within each column of X.
    The result is a matrix with the same shape as X.

    If X is a dictionary, the ranking is based on its values, and the ranks of
    all elements are returned.

    Unlike denseRank, rank skips positions after equal rankings.

    Parameters
    ----------
    X : Constant
        A vector/matrix/dictionary.
    ascending : Constant, optional
        A Boolean value indicating whether to sort in ascending order. The default value is true.
    ignoreNA : Constant, optional
        A Boolean value indicating whether null values are ignored in ranking.
        The default value is true. If set to false, null values are ranked as the minimum value.
    percent : Constant, optional
        A Boolean value, indicating whether to display the returned rankings in percentile form.
        The default value is false.
    """
    ...


@builtin_function(_derivative)
def derivative(func: Constant, X: Constant, dx: Constant = DFLT, n: Constant = DFLT, order: Constant = DFLT) -> Constant:
    r"""Return the derivative of func of order n at X.

    Parameters
    ----------
    func : Constant
        A unary function.
    X : Constant
        A numeric scalar/vector indicating where the derivative is evaluated.
    dx : Constant, optional
        A scalar of FLOAT type indicating spacing. The default value is 1.0.
    n : Constant, optional
        An integer scalar indicating the order of the derivative.
        As of now only n=1 is supported.
    order : Constant, optional
        An integer scalar indicating the number of points to use.
        It must be an odd number.
        The default value is 3 and can be values between 3 and 1023.
    """
    ...


@builtin_function(_det)
def det(obj: Constant) -> Constant:
    r"""Return the determinant of matrix X.
    Null values are replaced with 0 in the calculation.

    Parameters
    ----------
    X : Constant
        A matrix.
    """
    ...


@builtin_function(_diag)
def diag(X: Constant) -> Constant:
    r"""If X is a vector, return a diagonal matrix.

    If X is a square matrix, return a vector with the diagonal elements of the matrix.

    Parameters
    ----------
    X : Constant
        A numeric vector or a square matrix.
    """
    ...


@builtin_function(_dict)
def dict(keyType: Union[Alias[Literal["keyObj"]], Constant], valueType: Union[Alias[Literal["valueObj"]], Constant], ordered: Constant = DFLT) -> Constant:
    r"""Return a dictionary object.

    Parameters
    ----------
    keyType : Constant
        The data type of dictionary keys. The following data categories are
        supported: Integral (excluding COMPRESSED), Temporal, Floating and Literal.

    valueType : Constant
        The data type of dictionary values. Note that COMPLEX/POINT is not supported.

    ordered : Constant, optional
        A Boolean value. The default value is false, which indicates to create
        a regular dictionary. True means to create an ordered dictionary.
    """
    ...


@builtin_function(_dictUpdate_)
def dictUpdate_(dictionary: Constant, function: Constant, keys: Constant, parameters: Constant, initFunc: Constant = DFLT) -> Constant:
    r"""Update a dictionary for specified keys with the specified function.

    Parameters
    ----------
    dictionary : Constant
        A dictionary object.
    function : Constant
        A function object.
    keys : Constant
        A scalar/vector indicating for which keys to apply the function.
    parameters : Constant
        Are of the same size as keys. The arguments passed to the applied
        function are parameters and the initial values of the dictionary.
    initFunc : Constant, optional
        A unary function. If the update operation involves new keys that did not
        exist in the dictionary to be updated, execute initFunc for these keys.
        If initFunc is specified, the values of dictionary must be a tuple.
    """
    ...


@builtin_function(_difference)
def difference(X: Constant) -> Constant:
    r"""Return the last element minus the first element of a vector.
    If X is a scalar, it returns 0.

    Parameters
    ----------
    X : Constant
        A scalar/vector.
    """
    ...


@builtin_function(_differentialEvolution)
def differentialEvolution(func: Constant, bounds: Constant, X0: Constant = DFLT, maxIter: Constant = DFLT, popSize: Constant = DFLT, mutation: Constant = DFLT, recombination: Constant = DFLT, tol: Constant = DFLT, atol: Constant = DFLT, polish: Constant = DFLT, seed: Constant = DFLT) -> Constant:
    r"""Use the Differential Evolution algorithm to calculate the global minimum
    of a function with multiple variables.

    Parameters
    ----------
    func : Constant
        The objective function to be minimized. Note that the function must return a scalar.
    bounds : Constant
        A numeric matrix of shape (N, 2) indicating the bounds for parameters,
        where N is the number of parameters to be optimized.
    X0 : Constant, optional
        A numeric vector indicating the initial guess to the minimization.

        .. note::

            Each row in the bound parameter contains two values (min, max), which
            define the lower and upper limits for the parameter values specified by X0.

            X0 and bounds must have the same length, i.e., N = size(X0).

    maxIter : Constant, optional
        A non-negative integer indicating the maximum number of iterations.
        The default value is 1000.
    popSize : Constant, optional
        A positive integer specifying the multiplier for setting the total population size.
        The population contains popSize*(N - N_equal) individuals, where N_equal
        represents the number of parameters whose bounds are equal. The default value is 15.
    mutation : Constant, optional
        A numeric pair in the format of (min, max), indicating the range of the
        mutation constant. It should satisfy 0 <= min <= max < 2. The default value is (0.5, 1).
    recombination : Constant, optional
        A numeric scalar in [0, 1], indicating the recombination constant,
        also known as the crossover probability.
    tol : Constant, optional
        A non-negative floating-point scalar indicating the relative tolerance
        for convergence. The default value is 0.01.
    atol : Constant, optional
        A non-negative floating-point scalar indicating the absolute tolerance
        for convergence. The default value is 0. The algorithm terminates when
        stdev(population_energies) <= atol + tol * abs(mean(population_energies)),
        where population_energies is the vector consisting of objective function
        values for all individuals in the population.
    polish : Constant, optional
        A Boolean scalar indicating whether to polish the differential evolution
        result using the L-BFGS-B method. The default value is true.
    seed : Constant, optional
        An integer indicating the random seed used in the differential evolution
        algorithm, allowing users to reproduce the results. If unspecified (default),
        a non-deterministic random number generator is used.

    Returns
    -------
    Constant
        A dictionary containing the following keys:

        - xopt: A floating-point vector indicating the parameter values that minimize
          the objective function.

        - fopt: A floating-point scalar indicating the minimum value of the objective
          function, where fopt = f(xopt).

        - iterations: An integer indicating the number of iterations during the optimization
          process.

        - fcalls: An integer indicating the number of times the objective function is
          called during the optimization process.

        - converged: A Boolean scalar indicating whether the optimization result is converged.

          - true: The optimization result has been converged to below a preset tolerance
            and the algorithm terminates.

          - false: The algorithm terminates without converging after reaching the maximum
            number of iterations.
    """
    ...


@builtin_function(_digitize)
def digitize(x: Constant, bins: Constant, right: Constant = DFLT) -> Constant:
    r"""Return the indices of the bins to which each value in x belongs.
    The return value has the same data form as x.

    +-------+---------------+-------------------------------------+
    | right | order of bins | returned index i satisfies          |
    +=======+===============+=====================================+
    | false | increasing    | bins[i-1] <= x < bins[i]            |
    +-------+---------------+-------------------------------------+
    | true  | increasing    | bins[i-1] < x <= bins[i]            |
    +-------+---------------+-------------------------------------+
    | false | decreasing    | bins[i-1] > x >= bins[i]            |
    +-------+---------------+-------------------------------------+
    | true  | decreasing    | bins[i-1] >= x > bins[i]            |
    +-------+---------------+-------------------------------------+

    If values in x are beyond the bounds of bins, 0 (for values beyond left
    bound) or length of bins (for values beyond right bound) is returned.

    Parameters
    ----------
    x : Constant
        A scalar or vector of floating-point, integral, or DECIMAL type,
        indicating the value to be binned.
    bins : Constant
        A monotonically increasing or decreasing vector of floating-point,
        integral, or DECIMAL type, indicating the bins.
    right : Constant, optional
        A Boolean value indicating whether the intervals include the right or
        the left bin edge. Default behavior is right=false indicating that the
        interval includes the left edge.
    """
    ...


@builtin_function(_disableActivePartition)
def disableActivePartition(dbHandle: Constant) -> Constant:
    r"""Cancel the connection between the active database and the historical database.

    Parameters
    ----------
    dbHandle : Constant
        The handle of the historical database.
    """
    ...


@builtin_function(_disableTSDBAsyncSorting)
def disableTSDBAsyncSorting() -> Constant:
    r"""Data written to the TSDB cache engine are sorted by sortColumns. The
    tasks of writing and sorting data can be processed synchronously or asynchronously.
    Execute the command to disable asynchronous sorting mode. This command can
    only be executed by an administrator on a data node.
    """
    ...


@builtin_function(_distance)
def distance(X: Constant, Y: Constant) -> Constant:
    r"""Calculate the distance in meters between 2 points on the earth's surface.

    Parameters
    ----------
    X : Constant
        A POINT scalar/pair/vector representing points in the coordinate system of earth.
    Y : Constant
        A POINT scalar/pair/vector representing points in the coordinate system of earth.
    """
    ...


@builtin_function(_distinct)
def distinct(X: Constant) -> Constant:
    r"""Return the distinct elements from X.

    Parameters
    ----------
    X : Constant
        A vector or array vector.
    """
    ...


@builtin_function(_div)
def div(X: Constant, Y: Constant) -> Constant:
    r"""Return element-by-element division of X by Y.

    When X or Y is floating, it returns a floating value.

    When both X and Y are integers, div means integer division, which is the
    same as applying the floor function after division.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix. If X or Y is a pair/vector/matrix, the other is a scalar
        or a pair/vector/matrix of the same size.
    Y : Constant
        A scalar/pair/vector/matrix. If X or Y is a pair/vector/matrix, the other is a scalar
        or a pair/vector/matrix of the same size.
    """
    ...


@builtin_function(_dividedDifference)
def dividedDifference(X: Constant, Y: Constant, resampleRule: Constant, closed: Constant = DFLT, origin: Constant = DFLT, outputX: Constant = DFLT) -> Constant:
    r"""Resample X based on the specified resampleRule, closed and origin.
    Perform divided difference interpolation on Y based on the resampled X.

    If outputX is unspecified, return a vector of Y after the interpolation.

    If outputX=true, return a tuple where the first element is the vector of
    resampled X and the second element is a vector of Y after the interpolation.

    Parameters
    ----------
    X : Constant
        A strictly increasing vector of temporal type.
    Y : Constant
        A numeric vector of the same length as X.
    resampleRule : Constant
        A string.
    closed : Constant, optional
        A string indicating which boundary of the interval is closed.
        The default value is 'left' for all values of rule except for 'M',
        'A', 'Q', 'BM', 'BA', 'BQ', and 'W' which all have a default of 'right'.

        The default is 'right' if origin is 'end' or 'end_day'.
    origin : Constant, optional
        A string or a scalar of the same data type as X, indicating the timestamp
        where the intervals start. It can be 'epoch', start', 'start_day', 'end',
        'end_day' or a user-defined time object. The default value is 'start_day'.

        - 'epoch': origin is 1970-01-01

        - 'start': origin is the first value of the timeseries

        - 'start_day': origin is 00:00 of the first day of the timeseries

        - 'end': origin is the last value of the timeseries

        - 'end_day': origin is 24:00 of the last day of the timeseries
    outputX : Constant
        A Boolean value indicating whether to output the resampled X.
        The default value is false.
    """
    ...


@builtin_function(_dot)
def dot(X: Constant, Y: Constant) -> Constant:
    r"""Return the matrix multiplication of X and Y. If X and Y are vectors of
    the same length, return their inner product.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix. If both of X and Y are vectors, they must have
        the same length. If one of X and Y is a matrix, the other is a vector/matrix
        and their dimensions must satisfy the rules of matrix multiplication.
    """
    ...


@builtin_function(_double)
def double(X: Constant) -> Constant:
    r"""Convert the input to the data type of DOUBLE.

    Parameters
    ----------
    X : Constant
        Can be of any data type.
    """
    ...


@builtin_function(_drop)
def drop(obj: Constant, count: Constant) -> Constant:
    r"""If X is a vector, delete the first n or last n (if n is negative) elements.

    If X is a matrix, delete the first n or last n (if n is negative) columns.

    If X is a table, delete the first n or last n (if n is negative) rows.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    n : Constant
        An integer.
    """
    ...


@builtin_function(_dropColumns_)
def dropColumns_(table: Constant, colNames: Constant) -> Constant:
    r"""Delete one or multiple columns from a table. Note that deleting a partitioning
    column from a DFS table is not supported.

    Parameters
    ----------
    table : Constant
        A table object. It is an in-memory table or a DFS table (for OLAP engine only).
    colNames : Constant
        A STRING scalar/vector indicating a column name. If table is a DFS table,
        it must be a scalar.
    """
    ...


@builtin_function(_dropPartition)
def dropPartition(dbHandle: Constant, partitionPaths: Constant, tableName: Constant = DFLT, forceDelete: Constant = DFLT, deleteSchema : Constant = DFLT) -> Constant:
    r"""Delete data from one or multiple partitions from a DFS database.

    If tableName is specified: delete one or multiple partitions of the given table.

    If tableName is not specified: delete one or multiple partitions of all tables with this partition.

    Parameters
    ----------
    dbHandle : Constant
        A DolphinDB database handle.
    partitionPaths : Constant
        Can be specified in two ways:

        - By path: partitionPaths is a STRING scalar/vector indicating the path of one
          or multiple partitions. Each string must start with "/". For composite partitions,
          the path must include all partition levels.

        - By condition: partitionPaths is a scalar or vector indicating the value(s) in the
          partitioning column. The system will drop all partitions containing these values.
          For composite partitions, partitionPaths is a tuple where each element is a filtering
          condition for each partition level (starting from the first level). If you do not
          want to apply filtering at a certain partition level, leave the corresponding element
          empty.
    tableName : Constant
        A string indicating a table name. It can be left empty if the database chunk
        granularity is at DATABASE level (i.e., database: chunkGranularity = 'DATABASE').
        Otherwise, it is a required parameter.
    forceDelete : Constant, optional
        A Boolean value. If set to true, the specified partition(s) will be
        deleted even if the partition(s) is recovering. The default value is false.

        .. note::

            When using the dropPartition function with forceDelete=false, the number of
            available replicas for the chunks involved in the transaction must be greater
            than or equal to the configured dfsReplicationFactor.

    deleteSchema : Constant, optional
        A Boolean value. The default value is false, indicating that only the
        data in the selected partitions will be deleted, but the partition
        schema (which you can check with schema().partitionSchema) is kept.
        When the following conditions are satisfied, you can delete the schema
        of the selected partitions along with the partition data by setting
        deleteSchema to true:

        - There's only one table in the database.

        - The partitioning type of the database is VALUE.

        - For composite partitions, the first level of partitioning type must be VALUE, and
          only the first level of partitions are selected for deletion.
    """
    ...


@builtin_function(_dropna)
def dropna(X: Constant, byRow: Constant = DFLT, thresh: Constant = DFLT) -> Constant:
    r"""If X is a vector, delete all null values from X.

    If X is a matrix and byRow=true, delete all rows with null values.

    If X is a matrix and byRow=false, delete all columns with null values.

    If thresh is specified, each row or column (as specified by byRow) in the
    result must have at least thresh non-null values.

    Parameters
    ----------
    X : Constant
        A vector or matrix.
    byRow : Constant, optional
        A Boolean value. The default value is true.
    thresh : Constant, optional
        A positive integer.
    """
    ...


@builtin_function(_duration)
def duration(X: Constant) -> Constant:
    r"""Convert X to DURATION type which indicates the length of a time interval.

    .. note::

        The unit of the time interval used for grouping cannot be more granular
        than the unit of the temporal column.

        Time units are case-sensitive, for example, "M" means month and "m"
        means minute. If the unit of the time interval is M, use function month
        to convert the time column values to months.

        Data of DURATION type cannot participate in calculations. For example,
        comparisons between DURATION values (such as duration(20ms) >= duration(10ms))
        are not supported.

    Parameters
    ----------
    X : Constant
        A STRING scalar composed of an integer and a unit of time. It supports
        the following units of time: y, M, w, d, B, H, m, s, ms, us, ns, and
        trading calendar identifier consisting of four capital letters.
    """
    ...


@builtin_function(_dynamicGroupCumcount)
def dynamicGroupCumcount(membership: Constant, prevMembership: Constant, groupCount: Constant) -> Constant:
    r"""The attribute and category of an event are fixed in most cases. In some
    scenarios, the category of an event, however, will change dynamically. For
    example, when processing real-time tick data, users may judge whether an
    order (attribute) is a large or a small one (category) based on the cumulative
    volume to analyze capital flow. As real-time data continues to flow in, trading
    volume keeps increasing, and thus a small order may change to a large one.

    Function dynamicGroupCumcount is used in such scenarios to count the number
    of dynamically cumulative events of different categories.

    Details are as follows:

    - If membership = prevMembership, count remains unchanged.

    - If membership ≠ prevMembership, the count of corresponding group of membership
      increases by 1, and the count of corresponding group of prevMembership decreases
      by 1.

    - If prevMembership is a null value (the first record of each group), the count of
      corresponding group of membership increases by 1.

    Parameters
    ----------
    membership : Constant
        A vector, of which elements must be integers in the interval [0, groupCount),
        indicating tags for the record at the current timestamp.
    prevMembership : Constant
        A vector of INT type, of which elements can be null values (the first
        record of each group), indicating tags for the record at the previous
        timestamp of membership.
    groupCount : Constant
        An integer in the interval [2, 8], indicating the number of tags.

    Returns
    -------
    Constant
        A tuple of length groupCount. Each element is a vector of the same length
        as membership, which sequentially records the cumulative count of each tag.

        .. note::

            The index of the tuple matches the tags, which means that the count of tag
            0 is output to the vector at index 0 of the tuple.
    """
    ...


@builtin_function(_dynamicGroupCumsum)
def dynamicGroupCumsum(cumValue: Constant, prevCumValue: Constant, membership: Constant, prevMembership: Constant, groupCount: Constant) -> Constant:
    r"""The attribute and category of an event are fixed in most cases. In some
    scenarios, the category of an event, however, will change dynamically. For
    example, when processing real-time tick data, users may judge whether an
    order (attribute) is a large or a small one (category) based on the cumulative
    volume to analyze capital flow. As real-time data continues to flow in, trading
    volume keeps increasing, and thus a small order may change to a large one.

    Function dynamicGroupCumsum is used in such scenarios to obtain the
    cumulative sum of an indicator for events of different categories.

    Details are as follows:

    - If membership = prevMembership, count remains unchanged.

    - If membership ≠ prevMembership, the count of corresponding group of membership
      increases by cumValue, and the count of corresponding group of prevMembership
      decreases by preCumValue.

    - If prevMembership is a null value (the first record of each group), the count of
      corresponding group of membership increases by cumValue.

    Parameters
    ----------
    cumValue : Constant
        A numeric vector that records the cumulative value of the event at the
        current timestamp.
    prevCumValue : Constant
        A numeric vector, of which elements can be null values (the first record
        of each group), indicating the cumulative value of the event at the
        previous timestamp of cumValue.
    membership : Constant
        A vector of INT type, of which elements must be integers in the interval
        [0, groupCount), indicating tags for records at the current timestamp.
    prevMembership : Constant
        A vector of INT type, of which elements can be null value (the first record
        of each group), indicating tags for records at the previous timestamp of membership.
    groupCount : Constant
        An integer in the interval [2, 8], indicating the number of tags.

    Returns
    -------
    Constant
        A tuple of length groupCount. Each element is a vector of the same
        length as membership, which sequentially records the cumulative sum of
        an indicator (cumValue) for each tag.

        .. note::

            The index of the tuple matches the tags, which means that the count of tag
            0 is output at index 0 of the tuple.
    """
    ...


@builtin_function(_each)
def each(func: Constant, *args) -> Constant:
    r"""Apply a function (specified by func or operator) to each element of args / X / Y.

    - For matrices, calculate in each column;

    - For tables, calculate in each row;

    - For array vectors, calculate in each row;

    - For dictionaries, calculate each value.

    The data type and form of the return value are determined by each calculation
    result. It returns a vector or matrix if all calculation results have the
    same data type and form, otherwise it returns a tuple.

    Parameters
    ----------
    func : Constant
        A function.
    args : Constant
        The required parameters of func.
    operator : Constant
        A binary operator.
    X : Constant
        A pair/vector/matrix/table/array vector/dictionary.
    Y : Constant
        A pair/vector/matrix/table/array vector/dictionary.

        X and Y must have the same dimensions.
    """
    ...


@builtin_function(_eachAt)
def eachAt(X: Constant, index: Constant) -> Constant:
    r"""If index is a Boolean expression, returns the elements in X that satisfy
    the condition specified by index (i.e., index = true). If not, returns the
    elements in X with the corresponding index.

    If X is a function, index is used as an argument of X.

    Parameters
    ----------
    X : Constant
        A scalar/vector(including tuple and array vector)/matrix/table/dictionary/pair/unary function.
    index : Constant
        A Boolean expression/scalar/vector/tuple/array vector/pair.
    """
    ...


@builtin_function(_eachLeft)
def eachLeft(func: Constant, X: Constant, Y: Constant, assembleRule: Union[Alias[Literal["consistent"]], Constant] = DFLT) -> Constant:
    r"""Calculate func(X(i),Y) for each element of X.

    - X(i) is each element when X is a vector.

    - X(i) is each column when X is a matrix.

    - X(i) is each row when X is a table.

    - X(i) is each row when X is an array vector.

    - X(i) is each value when X is a dictionary.

    If func supports vector operation and the input is a vector, we should use
    the vector function/operator directly instead of the eachLeft template for
    better performance.

    Parameters
    ----------
    func : Constant
        A binary function.
    X : Constant
        A vector/matrix/table/array vector/dictionary.
    Y : Constant
        A vector/matrix/table/array vector/dictionary.
    assembleRule : Constant, optional
            Indicates how the results of sub-tasks are merged into the final result.
            It accepts either an integer or a string, with the following options:

            - 0 (or "D"): The default value, which indicates the DolphinDB rule.
              This means the data type and form of the final result are determined
              by all sub results. If all sub results have the same data type and form,
              scalars will be combined into a vector, vectors into a matrix, matrices
              into a tuple, and dictionaries into a table. Otherwise, all sub results
              are combined into a tuple.

            - 1 (or "C"): The Consistent rule, which assumes all sub results match
              the type and form of the first sub result. This means the first sub
              result determines the data type and form of the final output. The system
              will attempt to convert any subsequent sub results that don't match
              the first sub result. If conversion fails, an exception is thrown.
              This rule should only be used when the sub results' types and forms
              are known to be consistent. This rule avoids having to cache and
              check each sub result individually, improving performance.

            - 2 (or "U"): The Tuple rule, which directly combines all sub results
              into a tuple without checking for consistency in their types or forms.

            - 3 (or "K"): The kdb+ rule. Like the DolphinDB rule, it checks all
              sub results to determine the final output. However, under the kdb+ rule,
              if any sub result is a vector, the final output will be a tuple. In
              contrast, under the DolphinDB rule, if all sub results are vectors of
              the same length, the final output will be a matrix. In all other cases,
              the output of the kdb+ rule is the same as the DolphinDB rule.
    """
    ...


@builtin_function(_eachPost)
def eachPost(func: Constant, X: Constant, post: Constant = DFLT, assembleRule: Union[Alias[Literal["consistent"]], Constant] = DFLT) -> Constant:
    r"""Apply func over all pairs of consecutive elements of the object. It is
    equivalent to: F(X[0], X[1]), F(X[1], X[2]), ..., F(X[n], post).

    Parameters
    ----------
    func : Constant
        A binary function.
    X : Constant
        A vector/matrix/table. When X is a matrix, post must be a scalar or vector;
        when X is a table, post must be a scalar or table. When post is absent,
        the first element in the result would be NULL.
    post : Constant, optional
        Provides a post-value for the last element of X. Its type requirement
        depends on the form of X.
    assembleRule : Constant, optional
        Indicates how the results of sub-tasks are merged into the final result.
        It accepts either an integer or a string, with the following options:

            - 0 (or "D"): The default value, which indicates the DolphinDB rule.
              This means the data type and form of the final result are determined
              by all sub results. If all sub results have the same data type and
              form, scalars will be combined into a vector, vectors into a matrix,
              matrices into a tuple, and dictionaries into a table. Otherwise, all
              sub results are combined into a tuple.

            - 1 (or "C"): The Consistent rule, which assumes all sub results match
              the type and form of the first sub result. This means the first sub
              result determines the data type and form of the final output. The
              system will attempt to convert any subsequent sub results that don't
              match the first sub result. If conversion fails, an exception is thrown.
              This rule should only be used when the sub results' types and forms
              are known to be consistent. This rule avoids having to cache and
              check each sub result individually, improving performance.

            - 2 (or "U"): The Tuple rule, which directly combines all sub results
              into a tuple without checking for consistency in their types or forms.

            - 3 (or "K"): The kdb+ rule. Like the DolphinDB rule, it checks all
              sub results to determine the final output. However, under the kdb+ rule,
              if any sub result is a vector, the final output will be a tuple. In
              contrast, under the DolphinDB rule, if all sub results are vectors of
              the same length, the final output will be a matrix. In all other cases,
              the output of the kdb+ rule is the same as the DolphinDB rule.
    """
    ...


@builtin_function(_eachPre)
def eachPre(func: Constant, X: Constant, pre: Constant = DFLT, assembleRule: Union[Alias[Literal["consistent"]], Constant] = DFLT) -> Constant:
    r"""Apply func over all pairs of consecutive elements of X. It is equivalent
    to: F(X[0], pre), F(X[1], X[0]), ..., F(X[n], X[n-1]).

    Parameters
    ----------
    func : Constant
        A binary function.
    X : Constant
        A vector/matrix/table. When X is a matrix, pre must be a scalar or
        vector; when X is a table, pre must be a scalar or table. When pre is
        absent, the first element in the result would be NULL.
    pre : Constant, optional
        Provides an initial pre-value for the calculation. Its data form depends
        on the data form of X.
    assembleRule : Constant, optional
        Indicates how the results of sub-tasks are merged into the final result.
        It accepts either an integer or a string, with the following options:

        - 0 (or "D"): The default value, which indicates the DolphinDB rule.
          This means the data type and form of the final result are determined
          by all sub results. If all sub results have the same data type and
          form, scalars will be combined into a vector, vectors into a matrix,
          matrices into a tuple, and dictionaries into a table. Otherwise, all
          sub results are combined into a tuple.

        - 1 (or "C"): The Consistent rule, which assumes all sub results match
          the type and form of the first sub result. This means the first sub
          result determines the data type and form of the final output. The
          system will attempt to convert any subsequent sub results that don't
          match the first sub result. If conversion fails, an exception is
          thrown. This rule should only be used when the sub results' types
          and forms are known to be consistent. This rule avoids having to
          cache and check each sub result individually, improving performance.

        - 2 (or "U"): The Tuple rule, which directly combines all sub results
          into a tuple without checking for consistency in their types or forms.

        - 3 (or "K"): The kdb+ rule. Like the DolphinDB rule, it checks all
          sub results to determine the final output. However, under the kdb+
          rule, if any sub result is a vector, the final output will be a
          tuple. In contrast, under the DolphinDB rule, if all sub results are
          vectors of the same length, the final output will be a matrix. In all
          other cases, the output of the kdb+ rule is the same as the DolphinDB rule.
    """
    ...


@builtin_function(_eachRight)
def eachRight(func: Constant, X: Constant, Y: Constant, assembleRule: Union[Alias[Literal["consistent"]], Constant] = DFLT) -> Constant:
    r"""Calculate func(X, Y(i)) for each element of Y.

    - Y(i) is each element when Y is a vector.

    - Y(i) is each column when Y is a matrix.

    - Y(i) is each row when Y is a table.

    - Y(i) is each row when Y is an array vector.

    - Y(i) is each value when Y is a dictionary.

    If the function/operator supports vector operation and the input itself is a
    vector, we should avoid the eachRight template and use the vector function/
    operator directly instead for better performance.

    Parameters
    ----------
    func : Constant
        A binary function.
    X : Constant
        A vector/matrix/table/array vector/dictionary.
    Y : Constant
        A vector/matrix/table/array vector/dictionary.
    assembleRule : Constant, optional
        Indicates how the results of sub-tasks are merged into the final result.
        It accepts either an integer or a string, with the following options:

        - 0 (or "D"): The default value, which indicates the DolphinDB rule. This means
          the data type and form of the final result are determined by all sub results. If
          all sub results have the same data type and form, scalars will be combined into
          a vector, vectors into a matrix, matrices into a tuple, and dictionaries into a
          table. Otherwise, all sub results are combined into a tuple.

        - 1 (or "C"): The Consistent rule, which assumes all sub results match the type
          and form of the first sub result. This means the first sub result determines the
          data type and form of the final output. The system will attempt to convert any
          subsequent sub results that don't match the first sub result. If conversion fails,
          an exception is thrown. This rule should only be used when the sub results' types
          and forms are known to be consistent. This rule avoids having to cache and check
          each sub result individually, improving performance.

        - 2 (or "U"): The Tuple rule, which directly combines all sub results into a tuple
          without checking for consistency in their types or forms.

        - 3 (or "K"): The kdb+ rule. Like the DolphinDB rule, it checks all sub results to
          determine the final output. However, under the kdb+ rule, if any sub result is a
          vector, the final output will be a tuple. In contrast, under the DolphinDB rule, if
          all sub results are vectors of the same length, the final output will be a matrix.
          In all other cases, the output of the kdb+ rule is the same as the DolphinDB rule.
    """
    ...


@builtin_function(_eig)
def eig(A: Constant) -> Constant:
    r"""Calculate the eigenvalues and eigenvectors of A.

    The result of eig is the same as the result of numpy.linalg.eigh.

    Parameters
    ----------
    A : Constant
        A real symmetric matrix or a Hermitian matrix.

    Returns
    -------
    Constant
        A dictionary.
    """
    ...


@builtin_function(_ej)
def ej(leftTable: Constant, rightTable: Constant, matchingCols: Constant, rightMatchingCols: Constant = DFLT, leftFilter: Constant = DFLT, rightFilter: Constant = DFLT) -> Constant:
    r"""Return only the rows that have equivalent values for the matching columns.

    Parameters
    ----------
    leftTable/rightTable : Constant
        A table to be joined.
    matchingCols : Constant
        A string scalar/vector indicating matching columns.
    rightMatchingCols : Constant
        A string scalar/vector indicating all the matching columns in rightTable.
        This optional argument must be specified if at least one of the matching
        columns has different names in leftTable and rightTable. The joining column
        names in the result will be the joining column names from the left table.
    leftFilter/rightFilter : Constant
        A condition expression used as filter conditions for the columns in the
        left and right tables. Use "and" or "or" to join multiple conditions.

        .. note::

            If parameter leftTable / rightTable is specified as a dimension table or
            partitioned table, parameters leftFilter and rightFilter must not be specified.
    """
    ...


@builtin_function(_elasticNet)
def elasticNet(ds: Constant, yColName: Constant, xColNames: Constant, alpha: Constant = DFLT, l1Ratio: Constant = DFLT, intercept: Constant = DFLT, normalize: Constant = DFLT, maxIter: Constant = DFLT, tolerance: Constant = DFLT, positive: Constant = DFLT, swColName: Constant = DFLT, checkInput: Constant = DFLT) -> Constant:
    r"""Implement linear regression with elastic net penalty (combined L1 and L2 priors as regularizer).

    Minimize the following objective function:

    :math:`\displaystyle{\frac{1}{2*n_-samples}}* \Bigl\lVert{y - Xw} \Bigr\rVert_2^2 + alpha * l1Ratio\Bigl\lVert{w}\Bigr\rVert_1 + \displaystyle{\frac{alpha*(1-l1Ratio)}{2}}\Bigl\lVert{w}\Bigr\rVert_2^2`

    Parameters
    ----------
    ds : Constant
        An in-memory table or a data source usually generated by the sqlDS function.
    yColName : Constant
        A string indicating the column name of the dependent variable in ds.
    xColNames : Constant
        A STRING scalar/vector indicating the column names of the independent variables in ds.
    alpha : Constant, optional
        A floating-point number representing the constant that multiplies the
        L1-norm. The default value is 1.0.
    l1Ratio : Constant, optional
        A floating-point number between 0 and 1 indicating the mixing parameter.
        For l1Ratio = 0 the penalty is an L2 penalty; for l1Ratio = 1 it is an
        L1 penalty; for 0 < l1Ratio < 1, the penalty is a combination of L1 and
        L2. The default value is 0.5.
    intercept : Constant, optional
        A Boolean value indicating whether to include the intercept in the
        regression. The default value is true.
    normalize : Constant, optional
        A Boolean value. If true, the regressors will be normalized before
        regression by subtracting the mean and dividing by the L2-norm. If
        intercept=false, this parameter will be ignored. The default value is false.
    maxIter : Constant, optional
        A positive integer indicating the maximum number of iterations.
        The default value is 1000.
    tolerance : Constant, optional
        A floating-point number. The iterations stop when the improvement in the
        objective function value is smaller than tolerance. The default value is 0.0001.
    positive : Constant, optional
        A Boolean value indicating whether to force the coefficient estimates to
        be positive. The default value is false.
    swColName : Constant, optional
        A string indicating a column name of ds. The specified column is used as
        the sample weight. If it is not specified, the sample weight is treated as 1.
    checkInput : Constant, optional
        A Boolean value. It determines whether to enable validation check for
        parameters yColName, xColNames, and swColName.

        - If checkInput = true (default), it will check the invalid value for
          parameters and throw an error if the null value exists.

        - If checkInput = false, the invalid value is not checked.

        It is recommended to specify checkInput = true. If it is false, it must
        be ensured that there are no invalid values in the input parameters and
        no invalid values will be generated during intermediate calculations,
        otherwise the returned model may be inaccurate.
    """
    ...


@builtin_function(_elasticNetCV)
def elasticNetCV(ds: Constant, yColName: Constant, xColNames: Constant, alphas: Constant = DFLT, l1Ratio: Constant = DFLT, intercept: Constant = DFLT, normalize: Constant = DFLT, maxIter: Constant = DFLT, tolerance: Constant = DFLT, positive: Constant = DFLT, swColName: Constant = DFLT, checkInput: Constant = DFLT) -> Constant:
    r"""Implement linear regression with elastic net penalty using 5-fold
    cross-validation and return a model corresponding to the optimal parameters.

    Parameters
    ----------
    ds : Constant
        An in-memory table or a data source usually generated by the sqlDS function.
    yColName : Constant
        A string indicating the column name of the dependent variable in ds.
    xColNames : Constant
        A STRING scalar/vector indicating the column names of the independent variables in ds.
    alphas : Constant, optional
        A floating-point scalar or vector that represents the coefficient
        multiplied by the L1 norm penalty term. The default value is [0.01, 0.1, 1.0].
    l1Ratio : Constant, optional
        A floating-point number between 0 and 1 indicating the mixing parameter.
        For l1Ratio = 0 the penalty is an L2 penalty; for l1Ratio = 1 it is an
        L1 penalty; for 0 < l1Ratio < 1, the penalty is a combination of L1 and
        L2. The default value is 0.5.
    intercept : Constant, optional
        A Boolean value indicating whether to include the intercept in the
        regression. The default value is true.
    normalize : Constant, optional
        A Boolean value. If true, the regressors will be normalized before
        regression by subtracting the mean and dividing by the L2-norm. If
        intercept=false, this parameter will be ignored. The default value is false.
    maxIter : Constant, optional
        A positive integer indicating the maximum number of iterations.
        The default value is 1000.
    tolerance : Constant, optional
        A floating-point number. The iterations stop when the improvement in the
        objective function value is smaller than tolerance. The default value is 0.0001.
    positive : Constant, optional
        A Boolean value indicating whether to force the coefficient estimates to
        be positive. The default value is false.
    swColName : Constant, optional
        A string indicating a column name of ds. The specified column is used as
        the sample weight. If it is not specified, the sample weight is treated as 1.
    checkInput : Constant, optional
        A Boolean value. It determines whether to enable validation check for
        parameters yColName, xColNames, and swColName.

        - If checkInput = true (default), it will check the invalid value for
          parameters and throw an error if the null value exists.

        - If checkInput = false, the invalid value is not checked.

        It is recommended to specify checkInput = true. If it is false, it must
        be ensured that there are no invalid values in the input parameters and
        no invalid values will be generated during intermediate calculations,
        otherwise the returned model may be inaccurate.

    Returns
    -------
    Constant
        A dictionary containing the following keys:

        - modelName: the model name, which is "elasticNetCV" for this method

        - coefficients: the regression coefficients

        - intercept: the intercept

        - dual_gap: the dual gap

        - tolerance: the tolerance for the optimization

        - iterations: the number of iterations

        - xColNames: the column names of the independent variables in the data source

        - predict: the function used for prediction

        - alpha: the penalty term for cross-validation
    """
    ...


@builtin_function(_ema)
def ema(X: Constant, window: Constant, warmup: Constant = DFLT) -> Constant:
    r"""Calculate the Exponential Moving Average (ema) for X in a count-based sliding
    window of the given length.

    The calculation formula is as follows:

    - warmup=false:

      :math:`EMA(X)_k = \displaystyle{\frac{2}{n+1}}*X_k + \Bigl(1-\displaystyle{\frac{2}{n+1}}\Bigr)*EMA(X)_{k-1}`

    - warmup=true:

      :math:`EMA_k=\begin{cases}X_0,\quad\text{k=0}\\\frac{2}{size(X)+1}*X_k+(1-\frac{2}{size(X)+1})*EMA_{k-1}, \quad\text{size(X)<n}\\\frac{2}{n+1}*X_k+(1-\frac{2}{n+1})*EMA_{k-1}, \quad size(X)\geq n\end{cases}`

      where :math:`EMA_k` is the k-th exponential moving average, n is the length of sliding
      window, :math:`X_k` is the k-th element of the vector X.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    window : Constant
        A positive integer indicating the size of the sliding window.
    warmup : Constant
        A Boolean value. The default value is false, indicating that the first
        (window-1) elements windows return NULL. If set to true, elements in the
        first (window-1) windows are calculated based on the formula given in the details.
    """
    ...


@builtin_function(_enableActivePartition)
def enableActivePartition(dbHandle: Constant, activeDate: Constant, siteAlias: Constant) -> Constant:
    r"""Establish a connection between the active database and the historical database.

    Parameters
    ----------
    db : Constant
        The handle of the historical database.
    activeDate : Constant
        The date of the active database.
    setAlias : Constant
        The node alias for the active database.
    """
    ...


@builtin_function(_enableTSDBAsyncSorting)
def enableTSDBAsyncSorting() -> Constant:
    r"""Data written to the TSDB cache engine are sorted by sortColumns. The
    tasks of writing and sorting data can be processed synchronously or
    asynchronously. Execute the command to enable asynchronous sorting mode. The
    number of asynchronous threads is specified with configuration parameter
    TSDBAsyncSortingWorkerNum. This command can only be executed by an administrator
    on a data node. Please make sure the parameter TSDBAsyncSortingWorkerNum is
    configured greater than 0 before executing the command.

    It's recommended to enable asynchronous mode for a TSDB engine on a multi-core processor.
    """
    ...


@builtin_function(_encodeShortGenomeSeq)
def encodeShortGenomeSeq(X: Constant) -> Constant:
    r"""Encode DNA sequences made up of A, T, C, G letters. The encoding can
    reduce the storage space needed for DNA sequences and improve performance.

    .. note::

        When X is an empty string (""), the function returns 0.

        When X contains any character other than A, T, C, G (case-sensitive),
        the function returns NULL.

        When the length of X exceeds 28 characters, the function returns NULL.

    Parameters
    ----------
    X : Constant
        A scalar/vector of STRING/CHAR type.

    Returns
    -------
    Constant
        A LONG or FAST LONG vector
    """
    ...


@builtin_function(_endsWith)
def endsWith(X: Constant, str: Constant) -> Constant:
    r"""Check if X ends with str. If yes, return true; otherwise, return false.

    Parameters
    ----------
    X : Constant
        A STRING scalar/vector.
    str : Constant
        A STRING scalar/vector.
    """
    ...


@builtin_function(_enlist)
def enlist(X: Constant) -> Constant:
    r"""If X is a scalar, returns a vector.

    If X is a dictionary:

    - When the keys are strings, it returns a single-row table.

    - When the keys are non-strings, it returns a tuple.

    If X is a vector, tuple or of other data forms, returns a tuple.

    Parameters
    ----------
    X : Constant
        Can be of any data form.
    """
    ...


@builtin_function(_eq)
def eq(X: Constant, Y: Constant) -> Constant:
    r"""If neither X nor Y is a set, return the element-by-element comparison of X and Y.

    If X and Y are sets, check if X and Y are identical.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix/set. If X or Y is a pair/vector/matrix, the other is a
        scalar or a pair/vector/matrix of the same size.
    Y : Constant
        A scalar/pair/vector/matrix/set. If X or Y is a pair/vector/matrix, the other is a
        scalar or a pair/vector/matrix of the same size.
    """
    ...


@builtin_function(_eqFloat)
def eqFloat(X: Constant, Y: Constant, precision: Constant = DFLT) -> Constant:
    r"""Return the element-by-element comparison of X and Y with the given precision.

    Parameters
    ----------
    X : Constant
        A numeric scalar/vector/matrix. If X or Y is a vector/matrix, the other is a scalar
        or a vector/matrix of the same size.
    Y : Constant
        A numeric scalar/vector/matrix. If X or Y is a vector/matrix, the other is a scalar
        or a vector/matrix of the same size.
    precision : Constant
        A non-negative integer. FLOAT and DOUBLE types are compared up to precision digits
        after the decimal point.
    """
    ...


@builtin_function(_eqObj)
def eqObj(obj1: Constant, obj2: Constant, precision: Constant = DFLT) -> Constant:
    r"""Check if the data types and values of two objects are identical. Return
    true only if both data types and values are identical. Please note that
    eqObj returns false if values are identical but object types are different.
    This is different from fuction eq.

    When comparing floating point numbers, function eqObj determines whether the
    values of obj1 and obj2 are equal based on the result of abs(obj1-obj2)<=pow(10,-precision).

    Parameters
    ----------
    obj1 : Constant
        A scalar/pair/vector/matrix.
    obj2 : Constant
        A scalar/pair/vector/matrix.
    precision : Constant, optional
        A non-negative integer. FLOAT and DOUBLE types are compared up to
        precision digits after the decimal point.
    """
    ...


@builtin_function(_eqPercent)
def eqPercent(X: Constant, Y: Constant, toleranceLevel: Constant = DFLT) -> Constant:
    r"""Check element-wise equality of two inputs X and Y are equal within the
    specified toleranceLevel.

    Parameters
    ----------
    X : Constant
        A scalar, vector, pair, or matriX. Supported data types include BOOL, CHAR, SHORT,
        INT, LONG, FLOAT, DOUBLE, DECIMAL. Note: X and Y must be of the same form, and
        elements in X and Y can be of different data types.
    Y : Constant
        X and Y are two numbers to compare. They must be scalars, vectors, pairs, or matrices
        of the same shape. Supported data types include BOOL, CHAR, SHORT, INT, LONG, FLOAT,
        DOUBLE, DECIMAL. Note: X and Y must be of the same form, and elements in X and Y
        can be of different data types.
    toleranceLevel : Constant, optional
        A number in (0, 100), representing the tolerable percentage error. The
        default value is 0.0001. This means the absolute difference between the
        two elements must not exceed the toleranceLevel percentage of the
        absolute value of Y.

    Returns
    -------
    Constant
        A Boolean scalar.

        .. note::

            If the type of the input X or Y is not supported, the function returns the result of eqObj(X, Y).

            Null values are not equal to other values.

            Null values of different types are considered equal.
    """
    ...


@builtin_function(_erase_)
def erase_(obj: Constant, key: Union[Alias[Literal["filter"]], Constant]) -> Constant:
    r"""Eliminate elements from a set, or members from a dictionary, or rows from a table.

    Parameters
    ----------
    obj : Constant
        A set/dictionary/table.
    key : Constant
        The element to be deleted for a set; the keys of the members to be
        deleted for a dictionary; a piece of meta code with filtering conditions
        for a table.
    filter : Constant
        The element to be deleted for a set; the keys of the members to be
        deleted for a dictionary; a piece of meta code with filtering conditions
        for a table. For details about meta code, please refer to Metaprogramming.
    """
    ...


@builtin_function(_esd)
def esd(data: Constant, hybrid: Constant = DFLT, maxAnomalies: Constant = DFLT, alpha: Constant = DFLT) -> Constant:
    r"""Conduct anomaly detection with the Extreme Studentized Deviate test (ESD).

    Parameters
    ----------
    data : Constant
        A numeric vector.
    hybrid : Constant, optional
        A Boolean value indicating whether to use median and median absolute
        deviation to replace mean and standard deviation. The results are more
        robust if hybrid=true. The default value is false.
    maxAnomalies : Constant, optional
        A positive integer or a floating-point number between 0 and 0.5.
        The default value is 0.1.

        - If maxAnomalies is a positive integer, it must be smaller than the size of
          data. It indicates the upper bound of the number of anomalies.

        - If maxAnomalies is a floating-point number between 0 and 0.5, the upper
          bound of the number of anomalies is int(size(data) * maxAnomalies).
    alpha : Constant, optional
        A positive number indicating the significance level of the statistical
        test. A larger alpha means a higher likelihood of detecting anomalies.

    Returns
    -------
    Constant
        A table with 2 columns where column index records the subscript of
        anomalies in data and column anoms are the anomaly values.
    """
    ...


@builtin_function(_euclidean)
def euclidean(X: Constant, Y: Constant) -> Constant:
    r"""If X and Y are scalars or vectors, return the result of their Euclidean distance.

    If X or Y is a matrix, return a vector that is the result of the Euclidean distance
    between elements in each column. Note that if both X and Y are indexed matrices
    or indexed series, return the results of rows with the same label. Rows with
    different labels will be ignored.

    As with all other aggregate functions, null values are ignored in the calculation.

    Parameters
    ----------
    X : Constant
        A numeric scalar, or vector/matrix.
    Y : Constant
        A numeric scalar, or vector/matrix with the same size as X.
    """
    ...


@builtin_function(_eval)
def eval(expr: Constant) -> Constant:
    r"""Evaluate the given metacode.

    Parameters
    ----------
    X : Constant
        The metacode.
    """
    ...


@builtin_function(_ewmCorr)
def ewmCorr(X: Constant, com: Constant = DFLT, span: Constant = DFLT, halfLife: Constant = DFLT, alpha: Constant = DFLT, minPeriods: Constant = DFLT, adjust: Constant = DFLT, ignoreNA: Constant = DFLT, other: Constant = DFLT, bias: Constant = DFLT) -> Constant:
    r"""Calculate exponentially weighted moving correlation of X and other.

    Exactly one of the parameters com, span, halfLife and alpha must be specified.

    Parameters
    ----------
    X : Constant
        A numeric vector.
    com : Constant, optional
        A non-negative floating number and specifies decay in terms of center of
        mass. alpha=1/(1+com) where alpha is the decay factor.
    span : Constant, optional
        A positive floating number larger than 1 and specifies decay in terms of
        span. alpha=2/(span+1).
    halfLife : Constant, optional
        A positive floating number and specifies decay in terms of half-life.
        alpha=1-exp(log(0.5)/halfLife).
    alpha : Constant, optional
        A floating number between 0 and 1 and directly specifies decay.
    minPeriods : Constant, optional
        An integer indicating the minimum number of observations in window
        required to have a value (otherwise result is NULL). The default value is 0.
    adjust : Constant, optional
        A Boolean value. The default value is true.

        - If adjust=true, the weights are (1-alpha)^(n-1), (1-alpha)^(n-2), …,
          1-alpha, 1 divided by their sum.

        - If adjust=false, the weights are (1-alpha)^(n-1), (1-alpha)^(n-2)*alpha,
          (1-alpha)^(n-3)*alpha^2,…, (1-alpha)*alpha, alpha.
    ignoreNA : Constant, optional
        A Boolean value indicating whether to ignore missing values. The defaut
        value is false.
    other : Constant, optional
        A numeric vector of the same length as X.
    bias : Constant, optional
        A Boolean value indicating whether the result is biased. The default
        value is false, meaning the bias is corrected.
    """
    ...


@builtin_function(_ewmCov)
def ewmCov(X: Constant, com: Constant = DFLT, span: Constant = DFLT, halfLife: Constant = DFLT, alpha: Constant = DFLT, minPeriods: Constant = DFLT, adjust: Constant = DFLT, ignoreNA: Constant = DFLT, other: Constant = DFLT, bias: Constant = DFLT) -> Constant:
    r"""Calculate exponentially weighted moving covariance of X and other.

    Exactly one of the parameters com, span, halfLife and alpha must be specified.

    Parameters
    ----------
    X : Constant
        A numeric vector.
    com : Constant, optional
        A non-negative floating number and specifies decay in terms of center of
        mass. alpha=1/(1+com) where alpha is the decay factor.
    span : Constant, optional
        A positive floating number larger than 1 and specifies decay in terms of
        span. alpha=2/(span+1).
    halfLife : Constant, optional
        A positive floating number and specifies decay in terms of half-life.
        alpha=1-exp(log(0.5)/halfLife).
    alpha : Constant, optional
        A floating number between 0 and 1 and directly specifies decay.
    minPeriods : Constant, optional
        An integer indicating the minimum number of observations in window
        required to have a value (otherwise result is NULL). The default value is 0.
    adjust : Constant, optional
        A Boolean value. The default value is true.

        - If adjust=true, the weights are (1-alpha)^(n-1), (1-alpha)^(n-2), …,
          1-alpha, 1 divided by their sum.

        - If adjust=false, the weights are (1-alpha)^(n-1), (1-alpha)^(n-2)*alpha,
          (1-alpha)^(n-3)*alpha^2,…, (1-alpha)*alpha, alpha.
    ignoreNA : Constant, optional
        A Boolean value indicating whether to ignore missing values. The defaut
        value is false.
    other : Constant, optional
        A numeric vector of the same length as X.
    bias : Constant, optional
        A Boolean value indicating whether the result is biased. The default
        value is false, meaning the bias is corrected.
    """
    ...


@builtin_function(_ewmMean)
def ewmMean(X: Constant, com: Constant = DFLT, span: Constant = DFLT, halfLife: Constant = DFLT, alpha: Constant = DFLT, minPeriods: Constant = DFLT, adjust: Constant = DFLT, ignoreNA: Constant = DFLT, times: Constant = DFLT) -> Constant:
    r"""Calculate exponentially weighted moving average.

    Exactly one of the parameters com, span, halfLife and alpha must be specified.

    Parameters
    ----------
    X : Constant
        A numeric vector.
    com : Constant, optional
        A non-negative floating number and specifies decay in terms of center of
        mass. alpha=1/(1+com) where alpha is the decay factor.
    span : Constant, optional
        A positive floating number larger than 1 and specifies decay in terms of
        span. alpha=2/(span+1).
    halfLife : Constant, optional
        A positive floating number or a scalar of DURATION type specifying the
        half-life. alpha=1-exp(ln(2)/halfLife). If halfLife is a DURATION, the
        times must be specified with the same time unit.
    alpha : Constant, optional
        A floating number between 0 and 1 and directly specifies decay.
    minPeriods : Constant, optional
        An integer indicating the minimum number of observations in window
        required to have a value (otherwise result is NULL). The default value is 0.
    adjust : Constant, optional
        A Boolean value. The default value is true.

        - If adjust=true, the weights are (1-alpha)^(n-1), (1-alpha)^(n-2), …,
          1-alpha, 1 divided by their sum.

        - If adjust=false, the weights are (1-alpha)^(n-1), (1-alpha)^(n-2)*alpha,
          (1-alpha)^(n-3)*alpha^2,…, (1-alpha)*alpha, alpha.
    ignoreNA : Constant, optional
        A Boolean value indicating whether to ignore null values when calculating
        weights. The default value is false.

        Take [x0, NULL, x2] for example,

        - If ignoreNA = true,

          - adjust = false, the weights of x0 and x2 are 1-α and α.

          - adjust = true, the weights of x0 and x2 are 1-α and 1.

        - If ignoreNA = false,

          - adjust = false, the weights of x0 and x2 are (1-α)2 and α.

          - adjust = true, the weights of x0 and x2 are (1-α)2 and 1.

    times : Constant, optional
        A strictly increasing vector of temporal type, with the same length as X.
        Required only when halfLife is a DURATION, and must have the same unit as halfLife.

        .. note::

            If halfLife uses B (business day) or a trading calendar unit, times must
            be a vector of DATE type.
    """
    ...


@builtin_function(_ewmStd)
def ewmStd(X: Constant, com: Constant = DFLT, span: Constant = DFLT, halfLife: Constant = DFLT, alpha: Constant = DFLT, minPeriods: Constant = DFLT, adjust: Constant = DFLT, ignoreNA: Constant = DFLT, bias: Constant = DFLT) -> Constant:
    r"""Calculate exponentially weighted moving standard deviation.

    Exactly one of the parameters com, span, halfLife and alpha must be specified.

    Parameters
    ----------
    X : Constant
        A numeric vector.
    com : Constant, optional
        A non-negative floating number and specifies decay in terms of center of
        mass. alpha=1/(1+com) where alpha is the decay factor.
    span : Constant, optional
        A positive floating number larger than 1 and specifies decay in terms of
        span. alpha=2/(span+1).
    halfLife : Constant, optional
        A positive floating number and specifies decay in terms of half-life.
        alpha=1-exp(log(0.5)/halfLife).
    alpha : Constant, optional
        A floating number between 0 and 1 and directly specifies decay.
    minPeriods : Constant, optional
        An integer indicating the minimum number of observations in window
        required to have a value (otherwise result is NULL). The default value is 0.
    adjust : Constant, optional
        A Boolean value. The default value is true.

        - If adjust=true, the weights are (1-alpha)^(n-1), (1-alpha)^(n-2), …,
          1-alpha, 1 divided by their sum.

        - If adjust=false, the weights are (1-alpha)^(n-1), (1-alpha)^(n-2)*alpha,
          (1-alpha)^(n-3)*alpha^2,…, (1-alpha)*alpha, alpha.
    ignoreNA : Constant, optional
        A Boolean value indicating whether to ignore missing values. The defaut
        value is false.
    other : Constant, optional
        A numeric vector of the same length as X.
    bias : Constant, optional
        A Boolean value indicating whether the result is biased. The default
        value is false, meaning the bias is corrected.
    """
    ...


@builtin_function(_ewmVar)
def ewmVar(X: Constant, com: Constant = DFLT, span: Constant = DFLT, halfLife: Constant = DFLT, alpha: Constant = DFLT, minPeriods: Constant = DFLT, adjust: Constant = DFLT, ignoreNA: Constant = DFLT, bias: Constant = DFLT) -> Constant:
    r"""Calculate exponentially weighted moving variance.

    Exactly one of the parameters com, span, halfLife and alpha must be specified.

    Parameters
    ----------
    X : Constant
        A numeric vector.
    com : Constant, optional
        A non-negative floating number and specifies decay in terms of center of
        mass. alpha=1/(1+com) where alpha is the decay factor.
    span : Constant, optional
        A positive floating number larger than 1 and specifies decay in terms of
        span. alpha=2/(span+1).
    halfLife : Constant, optional
        A positive floating number and specifies decay in terms of half-life.
        alpha=1-exp(log(0.5)/halfLife).
    alpha : Constant, optional
        A floating number between 0 and 1 and directly specifies decay.
    minPeriods : Constant, optional
        An integer indicating the minimum number of observations in window
        required to have a value (otherwise result is NULL). The default value is 0.
    adjust : Constant, optional
        A Boolean value. The default value is true.

        - If adjust=true, the weights are (1-alpha)^(n-1), (1-alpha)^(n-2), …,
          1-alpha, 1 divided by their sum.

        - If adjust=false, the weights are (1-alpha)^(n-1), (1-alpha)^(n-2)*alpha,
          (1-alpha)^(n-3)*alpha^2,…, (1-alpha)*alpha, alpha.
    ignoreNA : Constant, optional
        A Boolean value indicating whether to ignore missing values. The defaut
        value is false.
    other : Constant, optional
        A numeric vector of the same length as X.
    bias : Constant, optional
        A Boolean value indicating whether the result is biased. The default
        value is false, meaning the bias is corrected.
    """
    ...


@builtin_function(_exists)
def exists(paths: Constant) -> Constant:
    r"""Check if the specified file(s) or folder(s) exist. It can be used in the
    distributed files system to check if the specified folder(s) exist.

    Parameters
    ----------
    path : Constant
        A STRING scalar/vector, indicating the path of file(s) or folder(s).
    """
    ...


@builtin_function(_exp)
def exp(X: Constant) -> Constant:
    r"""Apply the exponential function to all elements of X.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix/table.
    """
    ...


@builtin_function(_exp2)
def exp2(X: Constant) -> Constant:
    r"""Return 2 raised to the power of X.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix.

    Returns
    -------
    Constant
        A DOUBLE type.
    """
    ...


@builtin_function(_expm1)
def expm1(X: Constant) -> Constant:
    r"""Return exp(X)-1.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix/table.
    """
    ...


@builtin_function(_expr)
def expr(*args) -> Constant:
    r"""Generate metacode from args.

    Parameters
    ----------
    args... : Constant
        Objects, operators, or metacode. A metacode block contains objects or
        expressions enclosed by angle brackets < >. The minimum number of arguments is 2.
    """
    ...


@builtin_function(_extractTextSchema)
def extractTextSchema(filename: Constant, delimiter: Constant = DFLT, skipRows: Constant = DFLT) -> Constant:
    r"""Generate the schema table for the input data file. The schema table has 2
    columns: column names and their data types.

    When the input file contains dates and times:

    - For data with delimiters (date delimiters "-", "/" and ".", and time delimiter ":"),
      it will be converted to the corresponding type. For example, "12:34:56" is converted
      to the SECOND type; "23.04.10" is converted to the DATE type.

    - For data without delimiters, data in the format of "yyMMdd" that meets 0<=yy<=99,
      0<=MM<=12, 1<=dd<=31, will be preferentially parsed as DATE; data in the format of
      "yyyyMMdd" that meets 1900<=yyyy<=2100, 0<=MM<=12, 1<=dd<=31 will be preferentially
      parsed as DATE.

    Parameters
    ----------
    filename : Constant
        The input data file name with its absolute path. Currently only .csv
        files are supported.
    delimiter : Constant, optional
        A string indicating the table column separator. It can consist of one or
        more characters, with the default being a comma (',').
    skipRows : Constant, optional
        An integer between 0 and 1024 indicating the rows in the beginning of
        the text file to be ignored. The default value is 0.
    """
    ...


@builtin_function(_eye)
def eye(n: Constant) -> Constant:
    r"""Return an X by X indentity matrix.

    Parameters
    ----------
    X : Constant
        A positive integer.
    """
    ...


@builtin_function(_fTest)
def fTest(X: Constant, Y: Constant, ratio: Constant = DFLT, confLevel: Constant = DFLT) -> Constant:
    r"""Conduct an F-test to compare the variances of two samples.

    Parameters
    ----------
    X : Constant
        A numeric vector indicating the first sample for the F-test.
    Y : Constant
        A numeric vector indicating the second sample for the F-test.
    ratio : Constant, optional
        A positive floating number indicating the ratio of the variances of X
        and Y in the null hypothesis. The default value is 1.
    confLevel : Constant, optional
        A floating number between 0 and 1 indicating the confidence level of the
        test. It is optional and the default value is 0.95.

    Returns
    -------
    Constant
        A dictionary with the following keys:

        - stat: a table with p-value and confidence interval under 3 alternative hypotheses

        - numeratorDf: degree of freedom of the numerator

        - denominatorDf: degree of freedom of the denominator

        - confLevel: confidence level

        - method: "F test to compare two variances"

        - fValue: F-stat
    """
    ...


@builtin_function(_ffill)
def ffill(obj: Constant, limit: Constant = DFLT) -> Constant:
    r"""If obj is a vector, forward fill the null values in obj with the previous
    non-null value.

    If obj is an array vector:

    - For an empty row, fill it with the nearest non-empty row that precedes it.

    - For null values in a column, fill them with the nearest non-null value that precedes it within the same column.

    If obj is a matrix or a table, forward fill the null values in each column
    of obj according to the above rules.

    This operation creates a new vector and does not change the input vector.
    Function ffill_ changes the input vector.

    .. note::

        The only difference between ffill and ffill_ is that the latter assigns
        the result to obj and thus changing the value of obj after the execution.

    Parameters
    ----------
    obj : Constant
        A vector/matrix/table or an array vector.
    limit : Constant, optional
        A positive integer that specifies the maximum number of consecutive null
        values to forward fill for each block of null values. limit is not
        supported when obj is an array vector.
    """
    ...


@builtin_function(_ffill_)
def ffill_(obj: Constant, limit: Constant = DFLT) -> Constant:
    r"""If obj is a vector, forward fill the null values in obj with the previous
    non-null value.

    If obj is a matrix or a table, forward fill the null values in each column
    of obj with the previous non-null value.

    .. note::

        The only difference between ffill and ffill_ is that the latter assigns
        the result to obj and thus changing the value of obj after the execution.

    Parameters
    ----------
    obj : Constant
        A vector/matrix/table.
    limit : Constant
        A positive integer that specifies the number of null values to forward
        fill for each block of null values.
    """
    ...


@builtin_function(_fill_)
def fill_(obj: Constant, index: Constant, value: Constant) -> Constant:
    r"""Assign value to the elements of obj at index. It is equivalent to obj[index]=value.

    Parameters
    ----------
    obj : Constant
        A vector, tuple, matrix, dictionary or table.
    index : Constant
        If obj is a vector, tuple or matrix, index is an integer scalar/vector;

        If obj is a dictionary, index is a string scalar/vector indicating dictionary keys;

        If obj is a table, index is a string scalar/vector indicating column names.
    value : Constant
        A scalar/vector.
    """
    ...


@builtin_function(_find)
def find(X: Constant, Y: Constant) -> Constant:
    r"""If X is a vector: for each element of Y, return the position of its first
    occurrence in vector X. If the element doesn't appear in X, return -1. (To
    find the positions of all occurences, please use function at.)

    If X is a dictionary: for each element of Y, if it is a key in X, return the
    corresponding value in X; if it is not a key in X, return NULL.

    If X is an in-memory table with one column: for each element of Y, return
    the position of its first occurrence in the column of X. If the element
    doesn't appear in X, return -1. Note the column cannot be of array vector form.

    If X is a keyed table or indexed table: for each element of Y, return the
    position of its first occurrence in the key columns of X. If the element
    doesn't appear in the key columns of X, return -1.

    Parameters
    ----------
    X : Constant
        A vector, dictionary, in-memory table with one column, keyed table, or
        indexed table.
    Y : Constant
        A scalar, vector, matrix, tuple, dictionary, or table.
    """
    ...


@builtin_function(_first)
def first(X: Constant) -> Constant:
    r"""Return the first element of a vector, or the first row of a matrix or table.

    If the first element is a null value, the function returns NULL. To get the
    first non-null element, use firstNot.

    Parameters
    ----------
    X : Constant
        A scalar, pair, vector, matrix or table.
    """
    ...


@builtin_function(_firstHit)
def firstHit(func: Constant, X: Constant, target: Constant) -> Constant:
    r"""Return the first element in X that satisfies the condition X func target
    (e.g. X>5). If no element in X satisfies the condition, return a NULL vlaue.

    Null values are ignored in firstHit. Use firstNot to find the first non-null
    value.

    Parameters
    ----------
    func : Constant
        Can only be the following operators: >, >=, <, <=, !=, <>, ==.
    X : Constant
        A vector/matrix/table.
    target : Constant
        A scalar of the same type as X indicating the value to be compared with X.
    """
    ...


@builtin_function(_firstNot)
def firstNot(X: Constant, k: Constant = DFLT) -> Constant:
    r"""If X is a vector:

    - If k is not specified: return the first element of X that is not null.

    - If k is specified: return the first element of X that is neither k nor null.

    If X is a matrix or table, conduct the aforementioned calculation within
    each column of X. The result is a vector.

    Parameters
    ----------
    X : Constant
        A scalar, pair, vector, matrix or table.
    k : Constant, optional
        A scalar.
    """
    ...


@builtin_function(_fixedLengthArrayVector)
def fixedLengthArrayVector(*args) -> Constant:
    r"""Concatenate vectors, matrices, and tables.

    .. note::

        The length of a vector or each vector in a tuple, and the number of rows
        of a matrix or table must be the same.

    Parameters
    ----------
    args : Constant
        Vectors, tuples, fixed length array vectors, matrices, or tables. All
        args must be of the same data type supported by array vectors.

    Returns
    -------
    Constant
        An array vector.
    """
    ...


@builtin_function(_fj)
def fj(leftTable: Constant, rightTable: Constant, matchingCols: Constant, rightMatchingCols: Constant = DFLT, leftFilter: Constant = DFLT, rightFilter: Constant = DFLT) -> Constant:
    r"""Return all rows from equi join together with rows that are not matched
    from either the left table or the right table.

    Parameters
    ----------
    leftTable / rightTable : Constant
        The table to be joined.
    matchingCols : Constant
        A string scalar/vector indicating matching columns.
    rightMatchingCols : Constant
        A string scalar/vector indicating all the matching columns in rightTable.
        This optional argument must be specified if at least one of the matching
        columns has different names in leftTable and rightTable . The joining column
        names in the result will be the joining column names from the left table.
    """
    ...


@builtin_function(_flatten)
def flatten(X: Constant, depthFirst: Constant = DFLT) -> Constant:
    r"""Convert X into a 1D vector.

    Note that for a tuple:

    - If it contains tuple elements, flatten converts these elements to 1D vectors and
      retains other elements, returns a tuple.

    - If it does not contain tuple elements, flatten returns a 1D vector.

    Parameters
    ----------
    X : Constant
        A vector, tuple or matrix.
    """
    ...


@builtin_function(_flip)
def flip(obj: Constant) -> Constant:
    r"""Alias for transpose, used to transpose X:

    - If X is a tuple: return a tuple of the same length as each element of X. The n-th
      element of the result is a vector composed of the n-th element of each element of X.

    - If X is a matrix: return the transpose of X.

    - If X is a table: convert X into an ordered dictionary. The dictionary keys are column
      names. Each dictionary value is a vector of the corresponding column.

    - If X is a dictionary: convert X into a table. The dictionary keys must be of STRING type:

      - When values are scalars or vectors of equal length, the keys of X serve as the column
        names and the cooresponding values populate the column values in the table.

      - When the values are dictionaries, the resulting table will have the keys of X as the
        first column (named "key"). Subsequent columns will be derived from the keys of the
        first sub-dictionary with each row populated by corresponding values from all nested
        dictionaries. Missing keys in any sub-dictionary will result in null values in the table.

        .. note::

            Dictionaries with more than 32,767 keys cannot be converted into a table.

    - If X is an array vector or columnar tuple: switch data from columns to rows, or vice versa.

    Parameters
    ----------
    X : Constant
        A tuple/matrix/table/dictionary/array vector/columnar tuple.

        - If X is a tuple, all elements must be vectors of the same length.

        - If X is an array vector or columnar tuple, the number of elements in each row must be the same.
    """
    ...


@builtin_function(_floor)
def floor(X: Constant) -> Constant:
    r"""The floor and ceil functions map a real number to the largest previous
    and the smallest following integer, respectively. Function round maps a real
    number to the largest previous or the smallest following integer with the
    round half up rule.

    Parameters
    ----------
    X : Constant
        A scalar, vector, or matrix.
    """
    ...


@builtin_function(_flushOLAPCache)
def flushOLAPCache() -> Constant:
    r"""Flush the data of completed transactions cached in the OLAP cache engine
    to the database. Specify the configuration parameter chunkCacheEngineMemSize
    and set dataSync = 1 before execution.
    """
    ...


@builtin_function(_flushTSDBCache)
def flushTSDBCache() -> Constant:
    r"""Forcibly flush the completed transactions cached in the TSDB cache engine
    to the database. Specify the configuration parameter TSDBCacheEngineSize
    before execution.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_fmin)
    def fmin(func: Constant, X0: Constant, xtol: Constant = DFLT, ftol: Constant = DFLT, maxIter: Constant = DFLT, maxFun: Constant = DFLT) -> Constant:
        r"""Use a Nelder-Mead simplex algorithm to find the minimum of function
        of one or more variables. This algorithm only uses function values, not
        derivatives or second derivatives.

        Parameters
        ----------
        func : Constant
            The objective function to be minimized. The function must return a
            numeric scalar.
        X0 : Constant
            A numeric scalar or vector indicating the initial guess.
        xtol : Constant, optional
            A positive number specifying the absolute error in xopt between
            iterations that is acceptable for convergence.
        ftol : Constant, optional
            A positive number specifying the absolute error in func(xopt)
            between iterations that is acceptable for convergence. The default
            value is 0.0001.
        maxIter : Constant, optional
            A non-negative integer indicating the maximum number of iterations
            to perform.
        maxFun : Constant, optional
            A non-negative integer indicating the maximum number of function evaluations to make.

        Returns
        -------
        Constant
            A dictionary with the following keys:

            - xopt: a vector of floating-point numbers, indicating parameter that minimizes function.

            - fopt: a floating-point number, indicating value of function at minimum: fopt = f(xopt).

            - iterations: an integer, indicating number of iterations performed.

            - fcalls: an integer, indicating number of function calls made.

            - warnFlag: an integer that takes the following values

              - 0: Optimization algorithm completed.

              - 1: Maximum number of function evaluations made.

              - 2: Maximum number of iterations reached.
        """
        ...


if not sw_is_ce_edition():
    @builtin_function(_fminBFGS)
    def fminBFGS(func: Constant, X0: Constant, fprime: Constant = DFLT, gtol: Constant = DFLT, norm: Constant = DFLT, epsilon: Constant = DFLT, maxIter: Constant = DFLT, xrtol: Constant = DFLT, c1: Constant = DFLT, c2: Constant = DFLT) -> Constant:
        r"""Minimize a function using the BFGS algorithm.

        Parameters
        ----------
        func : Constant
            The function to minimize. The return value of the function must be
            numeric type.
        X0 : Constant
            A numeric scalar or vector indicating the initial guess.
        fprime : Constant, optional
            The gradient of func. If not provided, then func returns the function
            value and the gradient.
        gtol : Constant, optional
            A postive number. Iteration will terminates if gradient norm is less
            than gtol. The default value is 1e-5.
        norm : Constant, optional
            A positive number indicating the order of norm. Maximum norm is used
            by default.
        epsilon : Constant, optional
            A positive number indicating the step size used for numerically
            calculating the gradient. The default value is 1.4901161193847656e-08.
        maxIter : Constant, optional
            A non-negative integer indicating the maximum number of iterations.
            The default value is the size of X0 * 200.
        xrtol : Constant, optional
            A non-negative number indicating the relative tolerance. Iteration
            will terminate if step size is less than xk * xrtol where xk is the
            current parameter vector. The default value is 0.
        c1 : Constant, optional
            A number in (0,1) indicating the parameter for Armijo condition rule.
            The default value is 1e-4.
        c2 : Constant, optional
            A number in (0,1) indicating the parameter for curvature condition
            rule. The default value is 0.9. Note that c2 must be greater than c1.

        Returns
        -------
        Constant
            A dictionary with the following members:

            - xopt: A floating-point vector indicating the parameters of the minimum.

            - fopt: A floating-point scalar indicating the value of func at the minimum, i.e., fopt=func(xopt).

            - gopt: A floating-point vector indicating the gradient at the minimum. gopt=func'(xopt), which should be near 0.

            - Hinv: A floating-point matrix representing the inverse Hessian matrix.

            - iterations: Number of iterations.

            - fcalls: Number of function calls made.

            - gcalls: Number of gradient calls made.

            - warnFlag: An integer, which can be

              - 0: Minimization performed.

              - 1: Maximum number of iterations exceeded.

              - 2: Line search failed or extreme values encountered.

              - 3: Null result encountered.
        """
        ...


if not sw_is_ce_edition():
    @builtin_function(_fminLBFGSB)
    def fminLBFGSB(func: Constant, X0: Constant, fprime: Constant = DFLT, bounds: Constant = DFLT, m: Constant = DFLT, factr: Constant = DFLT, pgtol: Constant = DFLT, epsilon: Constant = DFLT, maxIter: Constant = DFLT, maxFun: Constant = DFLT, maxLS: Constant = DFLT) -> Constant:
        r"""Minimize a function func using the L-BFGS-B algorithm.

        Parameters
        ----------
        func : Constant
            The function to minimize. The return value of the function must be
            numeric type.
        X0 : Constant
            A numeric scalar or vector indicating the initial guess.
        fprime : Constant, optional
            The gradient of func. If not provided, then func returns the
            function value and the gradient (f, g = func(x, \*args)).
        bounds : Constant, optional
            A numeric matrix indicating the bounds on parameters of X0. The
            matrix must be in the shape of (N,2), where N=size(X0). The two
            elements of each row defines the bounds (min, max) on that parameter.
            float("inf") can be specified for no bound in that direction.
        m : Constant, optional
            A positive integer indicating the maximum number of variable metric
            corrections used to define the limited memory matrix. The default
            value is 10.
        factr : Constant, optional
            A positive number. Typical values for factr are: 1e12 for low
            accuracy; 1e7 (default) for moderate accuracy; 10.0 for extremely
            high accuracy.
        pgtol : Constant, optional
            A positive number. The default value is 1e-5.
        epsilon : Constant, optional
            A positive number indicating the step size used for numerically
            calculating the gradient. The default value is 1e-8.
        maxIter : Constant, optional
            A non-negative integer indicating the maximum number of iterations.
            The default value is 15000.
        maxFun : Constant, optional
            A non-negative integer indicating the maximum number of function
            evaluations. The default value is 15000.
        maxLS : Constant, optional
            A non-negative integer indicating the maximum number of line search
            steps (per iteration). The default value is 20.

        Returns
        -------
        Constant
            A dictionary with the following members:

            - xopt: A floating-point vector indicating the parameters of the minimum.

            - fopt: A floating-point scalar indicating the value of func at the minimum, i.e., fopt=func(xopt).

            - gopt: A floating-point vector indicating the gradient at the minimum, i.e., gopt=func'(xopt).

            - iterations: The number of iterations.

            - fcalls: The number of function calls made.

            - warnFlag: An integer, which can be

              - 0: Minimization performed.

              - 1: Maximum number of evaluations/iterations exceeded.

              - 2: Stopped for other reasons.
        """
        ...


if not sw_is_ce_edition():
    @builtin_function(_fminNCG)
    def fminNCG(func: Constant, X0: Constant, fprime: Constant, fhess: Constant, xtol: Constant = DFLT, maxIter: Constant = DFLT, c1: Constant = DFLT, c2: Constant = DFLT) -> Constant:
        r"""Perform unconstrained minimization of a function using the Newton-CG method.

        Parameters
        ----------
        func : Constant
            The function to minimize. The return value of the function must be
            numeric type.
        X0 : Constant
            A numeric scalar or vector indicating the initial guess.
        fprime : Constant
            The gradient of func.
        fhess : Constant
            The function to compute the Hessian matrix of func.
        xtol : Constant, optional
            A positive number. Convergence is assumed when the average relative
            error in the minimizer falls below this amount. The default value is
            1e-5.
        maxIter : Constant, optional
            A non-negative integer indicating the maximum number of iterations.
            The default value is 15000.
        c1 : Constant, optional
            A number in (0,1) indicating the parameter for Armijo condition rule.
            The default value is 1e-4.
        c2 : Constant, optional
            A number in (0,1) indicating the parameter for curvature condition
            rule. The default value is 0.9. Note that c2 must be greater than c1.

        Returns
        -------
        Constant
            A dictionary with the following members:

            - xopt: A floating-point vector indicating the parameters of the minimum.

            - fopt: A floating-point scalar indicating the value of func at the minimum, i.e., fopt=func(xopt).

            - iterations: The number of iterations.

            - fcalls: The number of function calls made.

            - hcalls: The number of Hessian calls made.

            - warnFlag: An integer, which can be

              - 0: Minimization performed.

              - 1: Maximum number of iterations exceeded.

              - 2: Line search failure (precision loss).

              - 3: Null result encountered.
        """
        ...


if not sw_is_ce_edition():
    @builtin_function(_fminSLSQP)
    def fminSLSQP(func: Constant, X0: Constant, fprime: Constant = DFLT, constraints: Constant = DFLT, bounds: Constant = DFLT, ftol: Constant = DFLT, epsilon: Constant = DFLT, maxIter: Constant = DFLT) -> Constant:
        r"""Minimize a function using Sequential Least Squares Programming.

        Parameters
        ----------
        func : Constant
            The function to minimize. The return value of the function must be
            numeric type.
        X0 : Constant
            A numeric scalar or vector indicating the initial guess.
        fprime : Constant, optional
            The gradient of func. If not provided, then func returns the function
            value and the gradient.
        constraints : Constant, optional
            A vector of dictionaries. Each dictionary should include the following keys:

            - type: A string indicating the constraint type, which can be 'eq' for equality
              constraints and 'ineq' for inequality constraints.

            - fun: The constraint function. The return value must be a numeric scalar or vector.

            - jac: The gradient function of constraint fun. The return value must be a numeric
              vector or a matrix. If the size of the return value of fun is m, and the size of
              the parameters to be optimized is n, then the shape of the return value of jac
              must be (n,m).

            .. note::

                The number of equality constraints in constraints cannot exceed the size
                of the parameters to be optimized. Let n be the number of parameters, k
                be the number of equality constraint functions, and leni be the size of
                the return value of the i-th equality constraint function.

        bounds : Constant, optional
            A numeric matrix indicating the bounds on parameters of X0. The
            matrix must be in the shape of (N,2), where N=size(X0). The two
            elements of each row defines the bounds (min, max) on that parameter.
            float("inf") can be specified for no bound in that direction.
        ftol : Constant, optional
            A positive number indicating the precision requirement for the
            function value when the optimization stops. The default value is 1e-6.
        epsilon : Constant, optional
            A positive number indicating the step size used for numerically
            calculating the gradient. The default value is 1.4901161193847656e-08.
        maxIter : Constant, optional
            A non-negative integer indicating the maximum number of iterations.
            The default value is 15000.

        Returns
        -------
        Constant
            A dictionary with the following keys:

            - xopt: A floating-point vector indicating the parameters of the minimum.

            - fopt: A floating-point scalar indicating the value of func at the minimum, i.e., fopt=func(xopt).

            - iterations: Number of iterations.

            - mode: An integer indicating the optimization state. mode=0 means optimization succeeded,
              while other values indicate abnormal algorithm termination.
        """
        ...


@builtin_function(_form)
def form(obj: Constant) -> Constant:
    r"""Generate the data form ID of a variable or a constant. Data form IDs and
    their corresponding data forms are: 0: scalar; 1: vector; 2: pair; 3: matrix;
    4: set; 5: dictionary; 6: table.

    Parameters
    ----------
    X : Constant
        A variable or constant.
    """
    ...


@builtin_function(_format)
def format(X: Constant, format: Constant) -> Constant:
    r"""Apply a specified format to the given object.

    Parameters
    ----------
    X : Constant
        A scalar/vector.
    format : Constant
        A string indicating the format to be applied to X. Depending on the data
        type of input X, format calls either function decimalFormat or temporalFormat.

    Returns
    -------
    Constant
        A STRING scalar/vector.
    """
    ...


@builtin_function(_fromJson)
def fromJson(jsonStr: Constant) -> Constant:
    r"""Converta a JSON string that complies with DolphinDB specification to a
    DolphinDB variable.

    A JSON string that complies with DolphinDB specification has at least the
    following 3 key-value pairs: form, type and value.

    For a table, the key-value pair 'name' can indicate column names.

    Parameters
    ----------
    X : Constant
        A JSON string that complies with DolphinDB specification.
    """
    ...


@builtin_function(_fromStdJson)
def fromStdJson(jsonStr: Constant) -> Constant:
    r"""Convert X to a DolphinDB variable. The following table shows the data
    form/type mappings.

    +---------+--------------------------------------------------+
    | JSON    | DolphinDB                                        |
    +=========+==================================================+
    | object  | Dictionary whose keys must be of STRING type,    |
    |         | and values can be of ANY type if multiple types  |
    |         | are converted.                                   |
    +---------+--------------------------------------------------+
    | array   | vector                                           |
    +---------+--------------------------------------------------+
    | string  | Convert to a Temporal value first. If fails, it  |
    |         | converts to a UTF-8 string.                      |
    +---------+--------------------------------------------------+
    | number  | DOUBLE                                           |
    +---------+--------------------------------------------------+
    | boolean | BOOL                                             |
    +---------+--------------------------------------------------+
    | null    | NULL                                             |
    +---------+--------------------------------------------------+

    .. note::

        Escape sequences will be automatically interpreted during conversion.

    Parameters
    ----------
    X : Constant
        A scalar or vector of standard JSON string(s).
    """
    ...


@builtin_function(_fromUTF8)
def fromUTF8(str: Constant, encode: Constant) -> Constant:
    r"""Convert the encoding of strings from UTF-8.

    Parameters
    ----------
    str : Constant
        A STRING scalar/vector.
    encode : Constant
        A string indicating the new encoding name. It must use lowercase.
    """
    ...


@builtin_function(_funcByName)
def funcByName(name: Constant) -> Constant:
    r"""Dynamically execute an operator or a function. It is mainly used in metaprogramming.

    Parameters
    ----------
    name : Constant
        A string indicating an operator or a function. The function can be
        either a built-in function or a user-defined function.
    """
    ...


@builtin_function(_fy5253)
def fy5253(X: Constant, weekday: Constant = DFLT, startingMonth: Constant = DFLT, nearest: Constant = DFLT, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""Using the 52-53 weeks in a fiscal year (4-4-5 calendar), it returns the
    start date of fiscal year which includes X.

    - If nearest=true, the last weekday which is closest to the last day of startingMonth
      will be used as the starting date of the fiscal year.

    - If nearest=false, the last weekday in startingMonth will be used as the starting
      date of the fiscal year.

    If offset is specified, it means that starting from the offset, the result
    will be updated every n years. Note that offset can take effect only when n
    is greater than 1.

    Parameters
    ----------
    X : Constant
        A scalar/vector. Its data type can be DATE, DATETIME, TIMESTAMP, or
        NANOTIMESTAMP.
    weekday : Constant, optional
        An integer between 0 and 6. 0 means Monday, 1 means Tuesday, …, and 6
        means Sunday. The default value is 0.
    startingMonth : Constant, optional
        An integer between 1 and 12 indicating the beginning month of a year.
        The default value is 1.
    nearest : Constant, optional
        A Boolean value. The default value is true.
    offset : Constant, optional
        A scalar with the same data type as X. It must be no greater than the
        minimum value in X. The default value is the minimum value in X.
    n : Constant, optional
        A positive integer.The default value is 1.
    """
    ...


@builtin_function(_fy5253Quarter)
def fy5253Quarter(X: Constant, weekday: Constant = DFLT, startingMonth: Constant = DFLT, qtrWithExtraWeek: Constant = DFLT, nearest: Constant = DFLT, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""Using the 52-53 week in fiscal year (4-4-5 calendar), this function
    returns the start date of fiscal year which includes X.

    - If nearest=true, the last weekday which is closest to the last day of startingMonth
      will be used as the starting date of the fiscal year.

    - If nearest=false, the last weekday in startingMonth will be used as the starting
      date of the fiscal year.

    If the offset is specified, indicating that starting from the offset, the
    result will be updated every n years. Note that only when n is greater than
    1, the offset can take effect.

    Parameters
    ----------
    X : Constant
        A scalar/vector, its type can be DATE, DATETIME, TIMESTAMP, NANOTIMESTAMP.
    weekday : Constant, optional
        An integer between 0 and 6. 0 means Monday, 1 means Tuesday, …, and 6
        means Sunday. The default value is 0.
    startingMonth : Constant, optional
        An integer between 1 and 12 indicating the beginning month of the year.
        The default value is 1.
    qtrWithExtraWeek : Constant, optional
        An integer between 1 to 4. If there is a leap quarter (usually the
        quarter contains 13 weeks, but the leap quarter contains 14 weeks ), it
        indicates the leap quarter.
    nearest : Constant, optional
        A Boolean value with the default value of true.
    offset : Constant, optional
        A scalar with the same data type as X. It must be smaller than the
        minimum value in X. The default value is the minimum value in X.
    n : Constant, optional
        A positive integer. The default value is 1.
    """
    ...


@builtin_function(_garch)
def garch(ds: Constant, endogColName: Constant, order: Constant, maxIter: Constant = DFLT) -> Constant:
    r"""Use the generalized autoregressive conditional heteroskedasticity (GARCH)
    model to model the conditional volatility of univariate time series.

    Parameters
    ----------
    ds : Constant
        An in-memory table or a vector consisting of DataSource objects,
        containing the multivariate time series to be analyzed. ds cannot be empty.
    endogColName : Constant
        A string indicating the column names of the endogenous variables in ds.
    order : Constant
        A positive integral vector of length 2 indicating the orders. For
        example, order=[1,2] means p=1, q=2 for a GARCH model, where p is the
        order of the GARCH terms and q is the order of the ARCH terms.
    maxIter : Constant, optional
        A positive integer indicating the maximum iterations. The default value
        is 50.

    Returns
    -------
    Constant
        A dictionary with the following keys:

        - volConstant: A floating-point scalar, representing the Vol Constant obtained
          through optimization.

        - returnsConstant: A floating-point scalar, representing the Returns Constant
          obtained through optimization.

        - archTerm: A floating-point vector, representing the ARCH Term obtained through
          optimization.

        - garchTerm: A floating-point vector, representing the GARCH Term obtained through
          optimization.

        - iterations: An integer representing the number of iterations.

        - aic: A floating-point scalar, representing the value of the AIC criterion.

        - bic: A floating-point scalar, representing the value of the BIC criterion.

        - nobs: An integer representing the number of observations in the time series, i.e.,
          the amount of data used for fitting.

        - model: A dictionary containing the basic information of the fitted model, with
          the following members:

          - order: A vector with 2 positive integers, representing the order of the model.

          - endog: A floating-point matrix, representing the observed data converted from ds.

          - coefficients: A floating-point vector, representing the values of the exogenous
            variables after fitting.

        - predict: The prediction function of the model. It can be called using model.predict(x), where:

          - model: A dictionary indicating the output of garch.

          - x: A positive integer representing the prediction step.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_gaussianKde)
    def gaussianKde(X: Constant, weights: Constant = DFLT, bwMethod: Constant = DFLT) -> Constant:
        r"""Estimate the probability density of the random variable using the
        Gaussian kernel from kernel density estimation (KDE).

        The generated model can be used as the input for the gaussianKdePredict
        function.

        Parameters
        ----------
        X : Constant
            A numeric vector, matrix, tuple, or table indicating the input
            dataset. Each row in X corresponds to a data point with consistent
            dimensions and a minimum of 2 elements (i.e., a data point must have
            at least 2 dimensions). The dataset must contain more rows than
            columns. Distributed tables are currently not supported.
        weights : Constant, optional
            A numeric vector indicating the weight of each data point. By
            default, all data points are equally weighted. The values in weights
            must be non-negative and not all zeros. The length of weights must
            be the same as the number of rows in X.
        bwMethod : Constant, optional
            Indicates the method for generating the bandwidth. It can be:

            - A STRING scalar, "scott" (default) or "silverman"

            - A numeric scalar indicating the bandwidth size

            - A function used to calculate the bandwidth based on X and return a numeric scalar.

        Returns
        -------
        Constant
            A dictionary with the following keys:

            - X is a floating-point vector or matrix indicating the input dataset X.

            - cov is a floating-point matrix indicating the Cholesky decomposition of the
              covariance matrix generated from weights, X, and bandwidth.

            - weights is a floating-point vector indicating the corresponding weight of each
              data point.

            - predict is a function pointer indicating the corresponding prediction function.
              It is used with the syntax model.gaussianKdePredict(model, X). For details, see gaussianKdePredict.

            - bandwidth is a floating-point scalar indicating the generated bandwidth.
        """
        ...


if not sw_is_ce_edition():
    @builtin_function(_gaussianKdePredict)
    def gaussianKdePredict(model: Constant, X: Constant) -> Constant:
        r"""Predict the probability density of the input data based on the model
        generated by gaussianKde.

        Parameters
        ----------
        model : Constant
            A dictionary indicating the model generated by gaussianKde.
        X : Constant
            A numeric vector, matrix, tuple, or table indicating the data to be
            predicted. Its dimensions must be the same as those of the dataset
            used in gaussianKde.

        Returns
        -------
        Constant
            A floating-point vector of the same size as the number of rows in X,
            indicating the prediction result of each data point in X.
        """
        ...


@builtin_function(_gaussianNB)
def gaussianNB(Y: Constant, X: Constant, varSmoothing: Constant = DFLT) -> Constant:
    r"""Conduct the Naive Bayesian classification.

    Parameters
    ----------
    Y : Constant
        A vector with the same length as table X. Each element of labels
        indicates the class that the correponding row in X belongs to.
    X : Constant
        A table indicating the training set. Each row is a sample and each
        column is a feature.
    varSmoothing : Constant, optional
        A positive floating number indicating the portion of the largest
        variance of all features that is added to variances for calculation
        stability. The default value is 1e-9.

    Returns
    -------
    Constant
        A dictionary with the following keys:

        - model: a RESOURCE data type variable. It is an internal binary resource
          generated by function gaussianNB and to be used by function predict.

        - modelName: string "GaussianNB".

        - varSmoothing: varSmoothing parameter value.
    """
    ...


@builtin_function(_ge)
def ge(X: Constant, Y: Constant) -> Constant:
    r"""If neither X nor Y is a set, return the element-by-element comparison of X>=Y.

    If both X and Y are sets, check if Y is a subset of X.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix/set.
    Y : Constant
        A scalar/pair/vector/matrix/set. If X or Y is a pair/vector/matrix, the
        other is a scalar or a pair/vector/matrix of the same size.
    """
    ...


@builtin_function(_gema)
def gema(X: Constant, window: Constant, alpha: Constant) -> Constant:
    r"""Calculate the Exponential Moving Average (ema) for X in a sliding window
    of the given length.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    window : Constant
        A positive integer indicating the size of the sliding window.
    alpha : Constant
        A floating-point number in (0,1) indicating the smoothing factor alpha.
    """
    ...


@builtin_function(_genShortGenomeSeq)
def genShortGenomeSeq(X: Constant, window: Constant) -> Constant:
    r"""This function slides a window of fixed size (based on the number of
    characters) over the input DNA sequence. It encodes the characters in each
    window and returns an integral vector containing the encoded values. The
    returned vector has the same length as the number of characters in X.

    .. note::

        This function adopts a forward sliding window approach, starting from
        the first character of the sequence. The sliding window moves by one
        character at a time. It first takes the current character, then the next
        character, continuing until window characters are included.

        If window exceeds the total length of X, an empty integral vector is
        returned.

    Parameters
    ----------
    X : Constant
        A STRING scalar or CHAR vector.
    window : Constant
        A positive integer in [2,28].

    Returns
    -------
    Constant
        +--------------+-------------------+
        | window Range | Return Type       |
        +==============+===================+
        | [2,4]        | FAST SHORT VECTOR |
        +--------------+-------------------+
        | [5,12]       | FAST INT VECTOR   |
        +--------------+-------------------+
        | [13,28]      | FAST LONG VECTOR  |
        +--------------+-------------------+
    """
    ...


@builtin_function(_genericStateIterate)
def genericStateIterate(X: Constant, initial: Constant, window: Constant, func: Constant) -> Constant:
    r"""This function performs calculation with count-based sliding windows iteratively.

    Suppose X is specified as [X1, X2, ..., Xn], column "factor" in the output
    table holds the calculation results, column "initial" is the initial column,
    window is set to "w", and the iterate function is "func". For the k-th
    record, the calculation rule is:

    - When w-0:

      - k=1: factor[0] = func(initial[0], X1[0], X2[0], … , Xn[0])

      - k>1: factor[k-1] = func(factor[(k-2)], X1[k-1], X2[k-1], … , Xn[k-1])

    - When w>0:

      - k <= w: factor[k-1] = initial[k-1]

      - k > w: factor[k-1] = func(factor[(k-1-w):k-1], X1[k-1], X2[k-1], … , Xn[k-1])

    Note that when a pair is used to indicate index, the right boundary is not
    inclusive, i.e., the range of (k-1-w):k-1 is [k-1-w, k-1).

    Parameters
    ----------
    X : Constant
        Can be column(s) from the input table, or the calculation results by
        applying a vector function to the column(s). You can set X to [] to
        leave it unspecified; or use a tuple to specify multiple columns for X.
    initial : Constant
        Can be a column from the input table, or the calculation results by
        applying a vector function to it. It is used to fill the first to
        window-th records in the output table.
    window : Constant
        A non-negative integer that specifies the window size (measured by the
        number of records).
    func : Constant
        A stateless user-defined function with one scalar as the return value.
        Arguments passed to func are as follows:

        - The first argument is a vector containing the previous window results if
          window>0, or the previous result if window=0.

        - Then followed by columns specified in X.

        - [Optional] Other fixed constants to be passed to func. In this case, you
          can fix the arguments with partial application.
    """
    ...


@builtin_function(_genericTStateIterate)
def genericTStateIterate(T: Constant, X: Constant, initial: Constant, window: Constant, func: Constant, leftClosed : Constant = DFLT) -> Constant:
    r"""This function performs calculation with time-based windows iteratively.

    Suppose T is a time column, X is [X1, X2, ..., Xn], column "factor" in the
    output table holds the calculation results, column "initial" is the initial
    column, window is set to "w", and the iterate function is "func".

    For the k-th record (with its timestamp Tk), the calculation rule is:

    - Tk ∈ [T1, T1+w): factor[k] = initial[k]

    - factor[k] = func(subFactor, X1[k], X2[k], … , Xn[k]), where

      - subFactor is the value of factor in the current window

      - the window for the (k+1)th record is (Tk-w, Tk] (when leftClosed=false) or
        [Tk-w, Tk] (when leftClosed=true).

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type. It cannot
        contain null values. Note that out-of-order data is discarded in the
        calculation.
    X : Constant
        Can be column(s) from the input table, or the calculation results by
        applying a vector function to the column(s). You can set X to [] to
        leave it unspecified; or use a tuple to specify multiple columns for X.
    initial : Constant
        The column used to fill the initial window in the result column of the
        output table. It can be a column from the input table, or the calculation
        results by applying a vector function to it. Suppose the timestamp of
        the first record is t0, the initial window is [t0, t0 + window),
        measured by time interval.
    window : Constant
        A positive integer or a DURATION scalar that specifies the window size.
        When window is an integer, it has the same time unit as T.
    func : Constant
        A stateless user-defined function with one scalar as the return value.
        Arguments passed to func are as follows:

        - The first argument is a vector containing the previous window results.

        - Then followed by columns specified in X.

        - [Optional] Other fixed constants to be passed to func. In this case, you
          can fix the arguments with partial application.
    leftClosed : Constant, optional
        A Boolean value indicating whether the left boundary of the window is
        inclusive. The default value is false.
    """
    ...


@builtin_function(_getBackupList)
def getBackupList(backupDir: Constant, dbPath: Constant, tableName: Constant) -> Constant:
    r"""Return a table with information about the backups of a DFS table. Each
    row of the table corresponds to a backed-up partition. The table contains
    the following columns:

    - chunkID: the chunk ID

    - chunkPath: the DFS path to database chunks

    - cid: the commit ID

    - rows: the number of records in a chunk

    - updateTime: the last update time

    Parameters
    ----------
    backupDir : Constant
        A string indicating the directory where the backup is saved.
    dbPath : Constant
        A string indicating the path of a distributed database.
    tableName : Constant
        A string indicating a distributed table name.
    """
    ...


@builtin_function(_getBackupMeta)
def getBackupMeta(backupDir: Constant, dbPath: Constant, partition: Constant, tableName: Constant) -> Constant:
    r"""Return a dictionary with information about the backup of a partition in a DFS table, which contains the following keys:

    - schema: the schema of the table

    - dfsPath: the DFS path to database chunks

    - rows: the number of records in a chunk

    - chunkID: the chunk ID

    - cid: the commit ID

    Parameters
    ----------
    backupDir : Constant
        A string indicating the directory where the backup is saved.
    dbPath : Constant
        A string indicating the path of a DFS database. For example: "dfs://demo".
    partition : Constant
        A string indicating the path of a partition under the database.
        For example: "/20190101/GOOG".
    tableName : Constant
        A string indicating a distributed table name.
    """
    ...


@builtin_function(_getBackupStatus)
def getBackupStatus(userName: Constant = DFLT) -> Constant:
    r"""Get the status of backup/restore tasks.

    Parameters
    ----------
    userName : Constant
        A string indicating the user name.

    Returns
    -------
    Constant
        A table where each row represents the information of a task.

        - userName: user name

        - type: backup/restore types.

          - BACKUP_BY_SQL/RESTORE_BY_SQL: backup/restore by SQL statement

          - BACKUP_BY_COPY_FILE/RESTORE_BY_COPY_FILE: backup/restore by copying files

        - startTime: when the task starts

        - dbName: database path

        - tableName: table name

        - totalPartitions: the number of partitions to be backed up/restored

        - completedPartitions: the number of partitions have been backed up/restored

        - percentComplete: the completion percentage

        - endTime: return the end time of a task if it has ended, otherwise return the
          estimated completion time

        - completed: whether the task is completed. Return 1 if it is completed, otherwise 0.

        .. note::

            The number of tasks generated for a backup statement is the same as
            the number of the backup partitions.

            Administrators can check the tasks submitted by all users, or the
            tasks submitted by a specified user by specifying a userName.

            When a non-administrator executes the function, return the status of
            backup/restore tasks submitted by the current user.
    """
    ...


@builtin_function(_getChunkPath)
def getChunkPath(ds: Constant) -> Constant:
    r"""Return the paths of the chunks that the given data sources represent.

    Parameters
    ----------
    ds : Constant
        One or multiple data sources.
    """
    ...


@builtin_function(_getChunksMeta)
def getChunksMeta(chunkPath: Constant = DFLT, top: Constant = DFLT) -> Constant:
    r"""Return metadata of specified database chunks on the local datanode. If
    chunkPath is not specified, return metadata of all database chunks on the
    local data node.

    Parameters
    ----------
    chunkPath : Constant, optional
        The DFS path to one or multiple database chunks. It supports wildcards %, * and ?.
    top : Constant, optional
        A positive number indicating the maximum number of chunks in the output.
        The default value is 1024. If it is set to -1, the number of returned
        chunks is not limited.

    Returns
    -------
    Constant
        A table containing the following columns:

        - site: Alias of the node

        - chunkId: The chunk ID

        - path: The path to database chunks

        - dfsPath: The DFS path to database chunks

        - type: The partition type. 0 for file chunk; 1 for tablet chunk.

        - flag: Flag for deletion.

          - flag=0: The chunk can be queried and accessed.

          - flag=1: The chunk has been logically marked as deleted and cannot be queried,
            but it has not been removed from disk.

        - size: The disk space (in bytes) occupied by the file chunk. It returns 0 for tablet
          chunks. Use the getTabletsMeta function to check the disk space tablet chunk occupies.

        - version: the version number

        - state: Chunk state.

          - 0 (final state): Transaction has been completed or rolled back.

          - 1 (before-commit state): The transaction is being executed on the chunk, such
            as writing or deleting data.

          - 2 (after-commit state): The transaction has been committed.

          - 3 (waiting-for-recovery state): When there is a version conflict or data corruption,
            this state occurs after the data node sends a recovery request to the controller
            and before the controller initiates the recovery.

          - 4 (in-recovery state): This state occurs after the controller receives the recovery
            request and initiates the recovery. Upon the completion of recovery, the chunk
            reverts to the final state (0).

        - versionList: version list.

        - resolved: Whether the transaction of the chunk is in the commit phase that needs to
          be resolved. True indicates the transaction is in the resolution phase or needs to
          be resolved; False indicates the transaction has already completed the resolution
          phase or it is not required.
    """
    ...


@builtin_function(_getLevelFileIndexCacheStatus)
def getLevelFileIndexCacheStatus() -> Constant:
    r"""Obtain the memory usage of the indexes of all level files.

    Returns
    -------
    Constant
        A dictionary with the following keys:

        - capacity: is the maximum size of level file index in the TSDB engine.

        - usage: is the size of the memory used (in bytes).
    """
    ...


@builtin_function(_getLicenseExpiration)
def getLicenseExpiration() -> Constant:
    r"""Return the expiration date of the license on the current node. It can be
    used to verify whether the license file has been updated.
    """
    ...


@builtin_function(_getMemoryStat)
def getMemoryStat() -> Constant:
    r"""Return the allocated memory and the unused memory.

    Returns
    -------
    Constant
        A dictionary with the following keys:

        - freeBytes: the allocated memory (in Bytes) for the current node.

        - allocatedBytes: the unused memory (in Bytes) for the current node.
    """
    ...


@builtin_function(_getOLAPCacheEngineStat)
def getOLAPCacheEngineStat() -> Constant:
    r"""Get the status of the OLAP cache engine on the current node. The function
    can only be called on the data node.

    Returns
    -------
    Constant
        A table containing the following columns:

        - chunkId: the chunk ID.

        - physicalName: the physical name of the table to which the chunk belongs.

        - timeSinceLastWrite: the time elapsed (in milliseconds) since last write.

        - cachedRowsOfCompletedTxn: the number of cached records of completed transactions.

        - cachedRowsOfUncompletedTxn: the number of cached records of uncompleted transactions.
          For each chunk, only the last transaction may not have been completed.

        - cachedMemOfCompletedTxn: the memory usage (in Bytes) of completed transactions.

        - cachedMemOfUncompletedTxn: the memory usage (in Bytes) of uncompleted transactions.

        - cachedTids: list of transaction IDs (tid).
    """
    ...


@builtin_function(_getOLAPCachedSymbolBaseMemSize)
def getOLAPCachedSymbolBaseMemSize() -> Constant:
    r"""Obtain the cache size (in Bytes) of SYMBOL base (i.e., a dictionary that
    stores integers encoded from the data of SYMBOL type) of the OLAP engine.
    """
    ...


@builtin_function(_getPKEYCompactionTaskStatus)
def getPKEYCompactionTaskStatus(count: Constant = DFLT) -> Constant:
    r"""Obtain the status of PKEY level file compaction tasks, including all
    pending tasks and completed tasks.The optional count limits the number of
    completed tasks returned. The function can only be executed on a data node.

    Parameters
    ----------
    count : Constant, optional
        A non-negative integer that specifies how many recent completed
        compaction tasks (successful or failed) to report per volume. The
        default value is 0, indicating that all completed compaction tasks are
        returned.

    Returns
    -------
    Constant
        A table with the following columns:

        - volume: the volume where the compaction is performed. It is set by the configuration
          parameter volumes.

        - level: the level of files that are involved in the current compaction. An empty
          cell means the compaction hasn't started, is ongoing, or failed.A compaction involves
          up to two levels at a time.

        - chunkId: the ID of chunk where the compaction is performed.

        - tableName: the physical name of the table where the compaction is performed.

        - files: the level files involved in the current compaction. An empty cell means the
          compaction hasn't started, is ongoing, or failed.

        - force: whether the compaction is triggered by triggerPKEYCompaction.

        - receivedTime: the timestamp when the compaction task enqueued.

        - startTime: the timestamp when the compaction task started.

        - endTime: the timestamp when the compaction task ended.

        - errorMessage: If a task failed, the column displays the failure cause; otherwise
          it is left empty.
    """
    ...


@builtin_function(_getPKEYMetaData)
def getPKEYMetaData() -> Constant:
    r"""Obtain the metadata of all chunks in the PKEY engine. The function can
    only be executed on a data node.

    Returns
    -------
    Constant
        A table with the following columns:

        - chunkId: the chunk ID

        - chunkPath: the physical path of the chunk

        - level: the file level

        - table: the table name

        - files: the level file name
    """
    ...


@builtin_function(_getRecoveryTaskStatus)
def getRecoveryTaskStatus() -> Constant:
    r"""Get the status of recovery tasks. This function can only be executed on
    a controller.

    Returns
    -------
    Constant
        A table containing the following columns:

        - TaskId: The job ID of the recovery task.

        - TaskType: The type of the recovery task. It can be "LoadRebalance" and "ChunkRecovery".

        - ChunkId: The chunk ID.

        - ChunkPath: The DFS path of the chunk.

        - Source: The source node for data recovery.

        - Dest: The destination node for data recovery.

        - Status: The status of the recovery task. It can be "Waiting", "In-Progress",
          and "Finished" or "Aborted".

        - AttemptCount: The number of recovery attempts that have been made.

        - DeleteSource: Whether to delete the replica on the source node. When TaskType is
          "ChunkRecovery", it is false. When TaskType is "LoadRebalance", it can be true or false.

        - StartTime: The time when the recovery task is created.

        - LastDequeueTime: The last time when the recovery task is dequeued.

        - LastStartTime: The last time when the recovery task started.

        - FinishTime: The time when the recovery task was finished.

        - IsIncrementalRecovery: Whether incremental replication is enabled.

        - IsAsyncRecovery: Whether asynchronous replication is enabled.

        - ChangeFromIncrementalToFull: Whether incremental replication has been changed to full
          replication. The recovery will be automatically changed to full recovery after multiple
          attempts for incremental recovery fail.

        - ChangeToSyncTime: The time when the online recovery is changed from asynchronous to
          synchronous.

        - FailureReason: The reason for the failure of the recovery tasks.
    """
    ...


@builtin_function(_getTSDBCachedSymbolBaseMemSize)
def getTSDBCachedSymbolBaseMemSize() -> Constant:
    r"""Obtain the cache size (in Bytes) of SYMBOL base (i.e., a dictionary that
    stores integers encoded from the data of SYMBOL type) of the TSDB engine.
    """
    ...


@builtin_function(_getTSDBCompactionTaskStatus)
def getTSDBCompactionTaskStatus(count: Constant = DFLT) -> Constant:
    r"""Obtain the status of TSDB level file compaction tasks. The function can
    only be executed on a data node.

    Parameters
    ----------
    count : Constant, optional
        A non-negative integer. Return the status of the latest count compaction
        tasks. The default value is 0, indicating that all completed compaction
        tasks (up to 256 latest tasks) and uncompleted tasks are returned.

    Returns
    -------
    Constant
        A table with the following columns:

        - volume: the volume where the compaction is performed. It is set by the configuration
          parameter volumes.

        - level: the level of files for compaction.

        - chunkId: the ID of chunk where the compaction is performed.

        - tableName: the physical name of the table where the compaction is performed.

        - files: the level files involved in the current compaction.

        - force: whether the compaction is triggered by triggerTSDBCompaction.

        - receivedTime: the timestamp when the compaction task enqueued.

        - startTime: the timestamp when the compaction task started.

        - endTime: the timestamp when the compaction task ended.

        - errorMessage: If a task failed, the column displays the failure cause; otherwise
          it is left empty.
    """
    ...


@builtin_function(_getTSDBDataStat)
def getTSDBDataStat(dbName: Constant = DFLT, tableName: Constant = DFLT, chunkId: Constant = DFLT) -> Constant:
    r"""Get the number of level files and sort key entries of specified chunks on
    the current node.

    Parameters
    ----------
    dbName : Constant, optional
        A string indicating the database name. It can contain wildcards ("*",
        "%", and "?"). The default value is "*".
    tableName : Constant, optional
        A string indicating the table name. It can contain wildcards ("*", "%",
        and "?"). The default value is "*".
    chunkId : Constant, optional
        A STRING scalar or vector indicating chunk ID(s). If chunkId is
        specified, dbName and tableName must be empty or “*”.
    "*" matches all; "?" matches a single character; "%" matches 0, 1 or more
    characters.

    Returns
    -------
    Constant
        A table containing the following columns:

        - levelFileCount: the number of level files of tables for each chunk.

        - sortKeyEntryCount: the number of sort key entries that has not been deduplicated
          in all level files for each chunk.
    """
    ...


@builtin_function(_getTSDBMetaData)
def getTSDBMetaData() -> Constant:
    r"""Obtain the metadata of all chunks in the TSDB engine. The function can
    only be executed on a data node.

    Returns
    -------
    Constant
        A table with the following columns:

        - chunkId: the chunk ID

        - chunkPath: the physical path of the chunk

        - level: the file level

        - table: the table name

        - files: the level file name
    """
    ...


@builtin_function(_getTSDBTableIndexCacheStatus)
def getTSDBTableIndexCacheStatus() -> Constant:
    r"""When querying a TSDB table, the indexes (including zonemap) of related
    level files will be loaded to the memory. This function is used to obtain
    the memory usage (in bytes) of the level file indexes for each loaded table.
    Combined with function getTSDBDataStat, it helps you to check whether the
    number of sort keys set for tables is reasonable.

    Returns
    -------
    Constant
        A table with the following columns:

        - dbName: the database name.

        - chunkId: the chunk ID.

        - tableName: the table name.

        - memUsage: the size of the memory used (in bytes).
    """
    ...


@builtin_function(_getTablet)
def getTablet(table: Constant, partition: Constant) -> Constant:
    r"""Return a table or a list of tables corresponding to the specified
    partition or partitions.

    - If partition is a scalar, return a table.

    - If partition is a vertor, return a tuple in which every element is a table.

    Parameters
    ----------
    table : Constant
        An in-memory partitioned table.
    partition : Constant
        A scalar/vector indicating a partition or partitions. If an element of
        partition belongs to the partitioning scheme of a partition, it
        represents the entire partition.
    """
    ...


@builtin_function(_getTabletsMeta)
def getTabletsMeta(chunkPath: Constant = DFLT, tableName: Constant = DFLT, diskUsage: Constant = DFLT, top: Constant = DFLT) -> Constant:
    r"""Return metadata of specified tablet chunks on the local node.

    Parameters
    ----------
    chunkPath : Constant, optional
        The DFS path to one or multiple database chunks. It supports wildcards %,
        * and ?.
    tableName : Constant, optional
        A string indicating a table name.
    diskUsage : Constant, optional
        A Boolean value indicating whether the result includes the column of diskUsage.
    top : Constant, optional
        A positive number indicating the maximum number of chunks in the output.
        The default value is 1024. To remove the upper limit of chunks in the
        output, set top to -1.

    Returns
    -------
    Constant
        A table with the following columns:

        - chunkId: the unique identifier of chunk.

        - path: the physical path of the partition.

        - dfsPath: the dfs path of the partition.

        - tableName: the table name.

        - version: the version number.

        - rowNum: the number of records in the partition.

        - createCids: the Cids created when updating/deleting the table.

        - latestPhysicalDir: the temporary physical directory storing the data generated
          by the operation with the latest Cid.

        - diskUsage: the disk space occupied by partition (in Bytes).
    """
    ...


@builtin_function(_glm)
def glm(ds: Constant, yColName: Constant, xColNames: Constant, family: Constant = DFLT, link: Constant = DFLT, tolerance: Constant = DFLT, maxIter: Constant = DFLT) -> Constant:
    r"""Fit a generalized linear model.

    Parameters
    ----------
    ds : Constant
        The data source to be trained. It can be generated with function sqlDS.
    yColName : Constant
        A string indicating the dependent variable column.
    xColNames : Constant
        A STRING scalar/vector indicating the names of the indepenent variable columns.
    family : Constant,
        A string indicating the type of distribution. It can be gaussian (default),
        poisson, gamma, inverseGaussian or binomial.
    link : Constant, optional
        A string indicating the type of the link function.

        Possible values of link and the dependent variable for each family:

        +-----------------+-----------------------------------+-----------------+----------------------+
        | family          | link                              | default link    | dependent variable   |
        +=================+===================================+=================+======================+
        | gaussian        | identity, inverse, log            | identity        | DOUBLE type          |
        +-----------------+-----------------------------------+-----------------+----------------------+
        | poisson         | log, sqrt, identity               | log             | non-negative integer |
        +-----------------+-----------------------------------+-----------------+----------------------+
        | gamma           | inverse, identity, log            | inverse         | y>=0                 |
        +-----------------+-----------------------------------+-----------------+----------------------+
        | inverseGaussian | inverseOfSquare, inverse, identity, log | inverseOfSquare | y>=0           |
        +-----------------+-----------------------------------+-----------------+----------------------+
        | binomial        | logit, probit                     | logit           | y=0,1                |
        +-----------------+-----------------------------------+-----------------+----------------------+

    tolerance : Constant, optional
        A numeric scalar. The iterations stops if the difference in the value of
        the log likelihood functions of 2 adjacent iterations is smaller than
        tolerance. The default value is 0.000001.
    maxIter : Constant, optional
        A positive integer indicating the maximum number of iterations. The
        default value is 100.

    Returns
    -------
    Constant
        A dictionary with the following keys: coefficients, link, tolerance,
        family, xColNames, tolerance, modelName, residualDeviance, iterations
        and dispersion.

        - coefficients is a table with the coefficient estimate, standard deviation, t
          value and p value for each coefficient;

        - modelName is "Generalized Linear Model";

        - iterations is the number of iterations;

        - dispersion is the dispersion coefficient of the model.
    """
    ...


@builtin_function(_gmm)
def gmm(X: Constant, k: Constant, maxIter: Constant = DFLT, tolerance: Constant = DFLT, randomSeed: Constant = DFLT, mean: Constant = DFLT, sigma: Constant = DFLT) -> Constant:
    r"""Train the Gaussian Mixture Model (GMM) with the given data set.

    Parameters
    ----------
    X : Constant
        The training data set. For univariate data, X is a vector; For multivariate
        data, X is a matrix/table where each column is a sample.
    k : Constant
        An integer indicating the number of independent Gaussians in a mixture model.
    maxlter : Constant, optional
        A positive integer indicating the maximum EM iterations to perform. The
        default value is 300.
    tolerance : Constant, optional
        A floating-point number indicating the convergence tolerance. EM iterations
        will stop when the lower bound average gain is below this threshold. The
        default value is 1e-4.
    randomSeed : Constant, optional
        The random seed given to the method.
    mean : Constant, optional
        A vector or matrix indicating the initial means.

        - For univariate data, it is a vector of length k;

        - For multivariate data, it is a matrix whose number of columns is k and number
          of rows is the same as the number of variables in X;

        - If mean is unspecified, k values are randomly selected from X as the initial means.
    sigma : Constant, optional
        Can be:

        - a vector, indicating the initialized variance of each submodel if X is univariate data;

        - a tuple of length k, indicating the covariance matrix of each submodel if X is
          multivariate data;

        - a vector with element values of 1 or an identity matrix if sigma is unspecified.

    Returns
    -------
    Constant
        A dictionary with the following keys:

        - modelName: a string "Gaussian Mixture Model"

        - prior: the prior probability of each submodel

        - mean: the expectation of each submodel

        - sigma: If X is univariate data, it represents the variance of each submodel;
          If X is multivariate data, it represents the covariance matrix of each submodel.
    """
    ...


@builtin_function(_gmtime)
def gmtime(X: Constant) -> Constant:
    r"""Convert X from local time zone to GMT (Greenwich Mean Time).

    Parameters
    ----------
    X : Constant
        A scalar or a vector. The data type of X can be DATETIME, TIMESTAMP, or
        NANOTIMESTAMP.
    """
    ...


@builtin_function(_gram)
def gram(ds: Constant, colNames: Constant = DFLT, subMean: Constant = DFLT, normalize: Constant = DFLT) -> Constant:
    r"""Calculate the Gram matrix of the selected columns in the given table.
    With a given matrix A, the result is A.tranpose() dot A.

    Parameters
    ----------
    ds : Constant
        One or multiple data source. It is usually generated by function sqlDS.
    colNames : Constant, optional
        A STRING vector indicating column names. The default value is all columns
        names in ds.
    subMean : Constant, optional
        A Boolean value indicating whether to substract from each column its mean.
        The default value is true.
    normalize : Constant, optional
        A Boolean value indicating whether to divide each column by its standard
        deviation. The default value is false.
    """
    ...


@builtin_function(_gramSchmidt)
def gramSchmidt(X: Constant, normalize : Constant = DFLT) -> Constant:
    r"""This function converts a matrix of full column rank into an orthogonal matrix.

    Parameters
    ----------
    X : Constant
        A matrix where each column (as a vector) is linearly independent, i.e.,
        the matrix has column full rank. It cannot contain any null values.
    normalize : Constant, optional
        A Boolean value indicating whether to output a normalized orthogonal
        matrix. The default value is false.

    Returns
    -------
    Constant
        A matrix of DOUBLE type.
    """
    ...


@builtin_function(_groupby)
def groupby(func: Constant, funcArgs: Constant, groupingCol: Constant) -> Constant:
    r"""For each group, calculate func(funcArgs) and return a scalar/vector/dictionary.

    Parameters
    ----------
    func : Constant
        A function. For the second use case, func can only have one parameter (funcArg).
    funcArgs : Constant
        A vector or a tuple with multiple vectors specifying the arguments of func.
    groupingCol : Constant
        A vector or a tuple with vectors of the same length indicating the
        grouping column(s). A grouping column and each argument in funcArgs are
        vectors of the same size.

    Returns
    -------
    Constant
        A table, where the number of rows is the same as the number of groups.
    """
    ...


@builtin_function(_groups)
def groups(X: Constant, mode: Constant = DFLT) -> Constant:
    r"""For each unique value in X, return the indices of all elements that hold
    the value.

    - If mode = "dict", return a dictionary.

    - If mode = "table", return a table with 2 columns, key and index. Each cell in the
      column index is an array vector.

    Parameters
    ----------
    X : Constant
        A vector.
    mode : Constant, optional
        Indicates the data form returned by the function. It can be:

        - "dict" (default): return a dictionary. The key of the dictionary stores the unique
          value in X; the value is a vector that stores the indices of all elements that
          hold the value.

        - "table": return a table with 2 columns, "key" and "index", storing the unique
          value in X and the corresponding indices.

        - "vector": return an array vector. The elements are the indices of each unique
          value in X, sorted in ascending order.

        - "tuple": return a tuple. The elements are stored the same as mode="vector".
    """
    ...


@builtin_function(_gt)
def gt(X: Constant, Y: Constant) -> Constant:
    r"""If neither X nor Y is a set, return the element-by-element comparison of X>Y.

    If both X and Y are sets, check if Y is a proper subset of X.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix/set.
    Y : Constant
        A scalar/pair/vector/matrix/set. If X or Y is a pair/vector/matrix, the
        other is a scalar or a pair/vector/matrix of the same size.
    """
    ...


@builtin_function(_hasNull)
def hasNull(obj: Constant) -> Constant:
    r"""For a scalar, return true if it is null.

    For a vector, return true if at least one element is null.

    For a matrix or a table, return true if at least one element of at least one
    column is null.

    Please refer to related functions: isNull, nullFill.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_hashBucket)
def hashBucket(X: Constant, buckets: Constant) -> Constant:
    r"""Hashes each element in X into one of the specified number of buckets and
    returns the corresponding bucket index.

    Parameters
    ----------
    X : Constant
        A scalar/vector.
    buckets : Constant
        A positive integer.
    """
    ...


@builtin_function(_head)
def head(obj: Constant, n: Constant = DFLT) -> Constant:
    r"""Return the first n element(s) of a vector, or the first n columns of a
    matrix, or the first n rows of a table.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    n : Constant, optional
        A positive integer. The default value is 1.
    """
    ...


@builtin_function(_hex)
def hex(X: Constant, reverse: Constant = DFLT) -> Constant:
    r"""Convert data of INTEGRAL, FLOAT, COMPLEX, and BINARY types to hexadecimal
    and return a string.

    Parameters
    ----------
    X : Constant
        An integer scalar/vector.
    reverse : Constant, optional
        A Boolean value indicating whether to reverse the order of the result.
        The default value is false.
    """
    ...


@builtin_function(_highDouble)
def highDouble(X: Constant) -> Constant:
    r"""It returns the high-order 8-byte double data of X.

    Parameters
    ----------
    X : Constant
        A vector/scalar which must be 16-byte data type.
    """
    ...


@builtin_function(_highLong)
def highLong(X: Constant) -> Constant:
    r"""It returns the high-order 8-byte long integer data of X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/table/pair/dictionary which must be 16-byte data type
        (UUID, IPADDR, INT128, COMPLEX, and POINT are supported).
    """
    ...


@builtin_function(_histogram2d)
def histogram2d(X: Constant, Y: Constant, bins: Constant = DFLT, range: Constant = DFLT, density: Constant = DFLT, weights: Constant = DFLT) -> Constant:
    r"""Compute the bi-dimensional histogram of two data samples.

    Parameters
    ----------
    X : Constant
        A numeric vector indicating the x coordinate of the points to be histogrammed.
        null values are not allowed.
    Y : Constant
        A numeric vector with the same length as X, indicating the y coordinates of the
        points to be histogrammed. null values are not allowed.
    bins : Constant, optional
        A numeric scalar, vector or a tuple. The default value is 10. Null
        values are not allowed. It can be:

        - Scalar: The number of bins for two dimensions.

        - Vector: The bin edges for the two diemensions. The vector must be strictly increasing.

        - Tuple with two scalars: The number of bins for each dimension.

        - Tuple with two vectors: The bin edges for each dimension.

        - Tuple with a scalar and a vector: The scalar represents the number of bins and
          the vector represents the bin edges, for the corresponding dimension.
    range : Constant, optional
        A tuple with two 2-length vectors, indicating the bin edges along each
        dimension (if not specified explicitly in the bins parameters). All
        values outside of this range will be considered outliers and not tallied
        in the histogram. The default value is null.
    density : Constant, optional
        A Boolean scalar. If false (default), returns the number of samples in
        each bin. If true, returns the probability density function at the bin,
        i.e., bin_count / sample_count / bin_area.
    weights : Constant, optional
        A numeric vector of the same length as X/Y for weighing each sample (x_i, y_i).
        The default value is null. Note that null values are not allowed in the vector.
        weights are normalized to 1 if density is true. Otherwise, the values of
        the returned histogram are equal to the sum of the weights belonging to
        the samples falling into each bin.

    Returns
    -------
    Constant
        A dictionary with the following keys:

        - H: The bi-dimensional histogram of samples x and y. Values in x are histogrammed
          along the first dimension and values in y are histogrammed along the second dimension.
          It is a matrix in the shape of (nx, ny), where nx and ny are the number of bins
          at each dimension.

        - xedges: A vector of length (nx+1) indicating the bin edges along the first dimension.

        - yedges: A vector of length (ny+1) indicating the bin edges along the second dimension.
    """
    ...


@builtin_function(_hour)
def hour(X: Constant) -> Constant:
    r"""Return the corresponding hour(s).

    Parameters
    ----------
    X : Constant
        A temporal scalar/vector.

    Returns
    -------
    Constant
        An integer.
    """
    ...


@builtin_function(_hourOfDay)
def hourOfDay(X: Constant) -> Constant:
    r"""For each element in X, return a number from 0 to 23 indicating which hour
    of the day it falls in.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type TIME, MINUTE, SECOND, DATETIME, TIMESTAMP,
        NANOTIME or NANOTIMESTAMP.
    """
    ...


@builtin_function(_ifNull)
def ifNull(X: Constant, Y: Constant) -> Constant:
    r"""Determine whether X is null. If it is null, return X; if not, return Y.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix.
    Y : Constant
        A scalar/pair/vector/matrix. X and Y must have the same data type.
    """
    ...


@builtin_function(_ifValid)
def ifValid(X: Constant, Y: Constant) -> Constant:
    r"""Determine whether X is valid. If it is valid, the value of X is returned;
    if it is null, the value of Y is returned.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix.
    Y : Constant
        A scalar/pair/vector/matrix. X and Y must have the same data type.
    """
    ...


@builtin_function(_ifirstHit)
def ifirstHit(func: Constant, X: Constant, target: Constant) -> Constant:
    r"""Return the index of the first element in X that satisfies the condition X
    func target (e.g. X>5).

    If no element in X satisfies the condition, return -1.

    Null values are ignored in ifirstHit.

    - Use ifirstNot to find the index of the first non-null value.

    - Use find to find the index of the first null value.

    Parameters
    ----------
    func : Constant
        Can only be the following operators: >, >=, <, <=, !=, <>, ==.
    X : Constant
        A vector/matrix/table.
    target : Constant
        A scalar of the same type as X indicating the value to be compared with X.
    """
    ...


@builtin_function(_ifirstNot)
def ifirstNot(X: Constant) -> Constant:
    r"""If X is a vector, return the subscript of the first non-null element.
    Return -1 if all elements are null.

    If X is a tuple of vectors, return the subscript of the first position where
    the element in all vectors is not null.

    If X is a matrix, return the subscript of the first non-null element within
    each column. The result is a vector.

    Parameters
    ----------
    X : Constant
        A vector, or a tuple of vectors of equal length, or a matrix.
    """
    ...


@builtin_function(_iif)
def iif(cond: Constant, trueResult: Constant, falseResult: Constant) -> Constant:
    r"""Performs an element-wise conditional operation, evaluating each element
    of the condition. Specifically, if cond[i] is true, it returns the i-th
    element of trueResult; otherwise, it returns the i-th element of falseResult.
    When cond[i] is a null value, it returns a null value.

    .. note::

        This function first parses the arguments and then returns trueResult or
        falseResult based on the result of cond.

    Parameters
    ----------
    cond : Constant
        A Boolean scalar/vector/matrix. It can be an expression returning
        Boolean values.
    trueResult : Constant
        A scalar/vector/tuple/matrix.
    falseResult : Constant
        A scalar/vector/tuple/matrix. trueResult and falseResult have the same
        number of elements as cond. Both must have the same data type.
    """
    ...


@builtin_function(_ilastNot)
def ilastNot(X: Constant) -> Constant:
    r"""If X is a vector, return the subscript of the last non-null element.
    Return -1 if all elements are null.

    If X is a tuple of vectors, return the subscript of the last position where
    the element in all vectors is not null.

    If X is a matrix, return the subscript of the last non-null element within
    each column. The result is a vector.

    Parameters
    ----------
    X : Constant
        A vector, or a tuple of vectors of equal length, or a matrix.
    """
    ...


@builtin_function(_ilike)
def ilike(X: Constant, pattern: Constant) -> Constant:
    r"""Return a Boolean value scalar or vector indicating whether each element
    in X fits a specific pattern. The comparison is case insensitive.

    The wildcard charater % indicates 0 or more characters.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix.
    pattern : Constant
        A string and is usually used with wildcard character %.
    """
    ...


@builtin_function(_imax)
def imax(X: Constant) -> Constant:
    r"""If X is a vector, return the position of the element with the largest
    value in X. If there are multiple identical maximum values, return the
    position of the first maximum value starting from the left.

    If X is a matrix, conduct the aforementioned calculation within each column
    of X. The result is a vector.

    Parameters
    ----------
    X : Constant
        A vector/matrix.
    """
    ...


@builtin_function(_imaxLast)
def imaxLast(X: Constant) -> Constant:
    r"""If X is a vector, return the position of the element with the largest
    value. If there are multiple elements with the identical largest value,
    return the position of the first element from the right. Same as other
    aggregate functions, null values are ignored.

    If X is a matrix, return a vector containing the position of the element
    with the largest value in each column.

    If X is a table, return a table. Each column of the table contains the
    position of the element with the largest value in the corresponding column of X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_imin)
def imin(X: Constant) -> Constant:
    r"""If X is a vector, return the position of the minimum value in a vector or
    a matrix. If there are multiple identical minimum values, return the position
    of the first minimum value starting from the left. As with all aggregate
    functions, null values are not included in the calculation.

    If X is a matrix, conduct the aforementioned calculation within each column
    of X. The result is a vector.

    Parameters
    ----------
    X : Constant
        A vector/matrix.
    """
    ...


@builtin_function(_iminLast)
def iminLast(X: Constant) -> Constant:
    r"""If X is a vector, return the position of the element with the smallest
    value. If there are multiple elements with the identical smallest value,
    return the position of the first element from the right. Same as other
    aggregate functions, null values are ignored.

    If X is a matrix, return a vector containing the position of the element
    with the smallest value in each column.

    If X is a table, return a table. Each column of the table contains the
    position of the element with the smallest value in the corresponding column
    of X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_imr)
def imr(ds: Constant, initValue: Constant, mapFunc: Constant, reduceFunc: Constant, finalFunc: Constant, terminateFunc: Constant, carryover: Constant = DFLT) -> Constant:
    r"""DolphinDB offers function imr for iterative computing based on the
    map-reduce methodology. Each iteration uses the result from the previous
    iteration and the input dataset. The input dataset for each iteration is
    unchanged so that it can be cached. Iterative computing requires initial
    values for the model parameters and a termination criterion.

    Parameters
    ----------
    ds : Constant
        The list of data sources. It must be a tuple with each element as a data
        source object. Even if there is only one data source, we still need a
        tuple to wrap the data source. In iterative computing, data sources are
        automatically cached and the cache will be cleared after the last iteration.
    initValue : Constant
        The initial values of model parameter estimates. The format of the initial
        values must be the same as the output of the final function.
    mapFunc : Constant
        The  map function. It has 2 or 3 arguments. The first argument is the
        data entity represented by the corresponding data source. The second
        argument is the output of the final function in the previous iteration,
        which is an updated estimate of the model parameter. For the first
        iteration, it is the initial values given by the user. The last argument
        is the carryover object. Please check the explanation for parameter
        carryover for details.
    reduceFunc : Constant, optional
        The binary reduce function combines two map function call results. If
        there are M map calls, the reduce function will be called M-1 times. The
        reduce function in most cases is trivial. An example is the addition function.
    finalFunc : Constant
        The final function in each iteration. It accepts two arguments. The first
        argument is the output of the final function in the previous iteration.
        For the first iteration, it is the initial values given by the user. The
        second argument is the output of the reduce function call. If the reduce
        function is not specified, a tuple representing the collection of
        individual map call results would be the second argument.
    terminateFunc : Constant
        Either a function that determines if the computation would continue, or
        a specified number of iterations. The termination function accepts two
        parameters. The first is the output of the reduce function in the previous
        iteration and the second is the output of the reduce function in the current
        iteration. If the function returns a true value, the iterations will end.
    carryover : Constant
        A Boolean value indicating whether a map function call produces a carryover
        object to be passed to the next iteration of the map function call. The
        default value is false. If it is set to true, the map function has 3
        arguments and the last argument is the carryover object, and the map
        function output is a tuple whose last element is the carryover object.
        In the first iteration, the carryover object is the null object.
    """
    ...


@builtin_function(_in)
def In(X: Constant, Y: Constant) -> Constant:
    r"""If Y is a scalar:

    - If Y is of temporal types, check if each element in X is equal to Y;

    - If Y is a scalar of other data types, check if X and Y are equal.

    If Y is a null value, return false.

    If Y is a vector, check if each element of X is an element in Y.

    If Y is a dictionary, check if each element of X is a key in the dictionary Y.

    If Y is an in-memory table with one column, check if each element of X appears
    in the column of Y. Note the column cannot be of array vector form.

    If Y is a keyed table or an indexed table, check if each element of X is a
    key of Y. The number of elements in X must equal the number of key columns of Y.

    Parameters
    ----------
    X : Constant
        A scalar/vector.
    Y : Constant
        A scalar, vector, dictionary, in-memory table with one column, keyed table,
        or indexed table.
    """
    ...


@builtin_function(_indexedSeries)
def indexedSeries(index: Constant, value: Constant) -> Constant:
    r"""indexedSeries supports alignment operations for panel data. When performing
    binary operations between matrices or vectors, calculations are performed on
    the corresponding elements, and the shape of these matrices or vectors must
    be the same.

    But when performing binary operations between indexed series or between
    indexed series and indexed matrix, the data is automatically aligned according
    to the row or column labels (index), and the shape of the matrices or series
    can be the same or not.

    The following binary operations are supported:

    - Arithmetic operators and functions: \+, \-, \*, \/(exact division), \\(ratio), \%(mod), pow

    - Logical operators and functions: \<, \<=, \>, \>=, \==, \!=, \<>, \&&, \||, \&, \|, \^

    - Sliding window functions: mwavg, mwsum, mbeta, mcorr, mcovar

    - Cumulative window functions: cumwavg, cumwsum, cumbeta, cumcorr, cumcovar

    - Aggregate functions: wavg, wsum, beta, corr, covar

    Parameters
    ----------
    index : Constant
        A vector.
    value : Constant
        A vector. *index* and *value* are vectors of the same length. *index* must be monotonically
        increasing with no duplicate values.
    """
    ...


@builtin_function(_indexedTable)
def indexedTable(*args) -> Constant:
    r"""Create an indexed table, which is a special type of in-memory table with
    primary key. The primary key can be one column or multiple columns. The indexed
    table uses a red-black tree to store the primary key index. During queries,
    as long as the query conditions include the first column of the primary key,
    data can be located through the index without performing a full table scan.
    It is recommended to use sliceByKey to improve query performance.

    When adding new records to the table, if the primary key of the new record
    duplicates an existing record, the system updates the record in the table;
    otherwise, the new record is added to the table.
    """
    ...


@builtin_function(_initcap)
def initcap(X: Constant) -> Constant:
    r"""The function returns an object of the same type/form as X.

    For words separated by delimiters, the first letter of each word is in
    uppercase, and all other letters are in lowercase. The delimiters can be any
    character other than letters or numbers, such as spaces, @, etc.

    .. note::

        Numbers are treated as letters.

    Parameters
    ----------
    X : Constant
        A STRING scalar/vector, or a SYMBOL vector.
    """
    ...


@builtin_function(_int)
def int(X: Constant) -> Constant:
    r"""Convert X to the data type of INT.

    Parameters
    ----------
    X : Constant
        Can be data of any types.
    """
    ...


@builtin_function(_int128)
def int128(X: Constant) -> Constant:
    r"""Convert STRING into INT128 data type.

    Parameters
    ----------
    X : Constant
        A string scalar/vector.
    """
    ...


@builtin_function(_integral)
def integral(func: Constant, start: Constant, end: Constant, start2: Constant = DFLT, end2: Constant = DFLT) -> Constant:
    r"""Return the integral of func from start to end.

    If the result is infinity or if the calculation involves complex numbers,
    the result is NULL.

    Parameters
    ----------
    func : Constant
        A unary function.
    start : Constant
        A numeric scalar/vector indicating start value. Null means negative infinity.
    end : Constant
        A numeric scalar/vector indicating end value. Null means positive infinity.
    start2 : Constant
        A numeric scalar/vector/unary function indicating the start value of the
        second dimension in double integral. Null means negative infinity.
    end2 : Constant
        A numeric scalar/vector/unary function indicating the end value of the second
        dimension in double integral. Null means positive infinity.

        - If both start and end are vectors, they must be of the same length.

        - If one of start and end is a scalar and the other is a vector, the scalar is
          treated as a vector of idential values.
    """
    ...


@builtin_function(_interpolate)
def interpolate(X: Constant, method: Constant = DFLT, limit: Constant = DFLT, inplace: Constant = DFLT, limitDirection: Constant = DFLT, limitArea: Constant = DFLT, index: Constant = DFLT) -> Constant:
    r"""Fills in null values in a numeric vector using interpolation. By default,
    the function treats each element's position (0, 1, 2, ..., size(X)-1) in X
    as its x-coordinate when performing the interpolation. You can also provide
    custom x-coordinates through the index parameter.

    Parameters
    ----------
    X : Constant
        A numeric vector.
    method : Constant, optional
        A string indicating how to fill the null values. It can take the following
        values and the default value is 'linear'.

        - 'linear': for null values surrounded by valid values, fill the null values linearly.
          For null values outside valid values, fill the null values with the closest valid values.

        - 'pad': fill null values with existing values.

        - 'nearest': fill null values with the closest valid values.

        .. note::

            When method = 'nearest' and limitDirection = 'both', if a null
            value is equidistant from nearest valid values on both sides, the
            system fills it using the value on the left.

        - krogh: fill null values with krogh polynomials.
    limit : Constant, optional
        A positive integer indicating the maximum number of consecutive null values
        to fill.
    inplace : Constant, optional
        A Boolean value indicating whether to update the input vector array. The
        default value is false, which means a new vector will be returned.
    limitDirection : Constant, optional
        A string indicating the direction to fill null values. It can take the
        following values: 'forward', 'backward' and 'both'. The default value is
        'forward'.
    limitArea : Constant, optional
        A string indicating restrictions regarding filling null values. It can
        take the following values and the default value is empty string "".

        - empty string: no restrictions.

        - inside: only fill null values surrounded by valid values.

        - outside: only fill null values outside valid values.
    index : Constant, optional
        Specifies a numeric or temporal vector that must have the same length as
        X and cannot contain null values. When index is provided, the function
        performs interpolation using these values as x-coordinates and X as
        y-coordinates to fill in any missing values in X.

    Returns
    -------
    Constant
        A numeric vector with null values filled in.
    """
    ...


@builtin_function(_intersection)
def intersection(X: Constant, Y: Constant) -> Constant:
    r"""If both X and Y are sets, return the intersection of the two sets.

    If X and Y are integer scalars/vectors, conduct the bitwise operation "AND".

    Parameters
    ----------
    X : Constant
        A set, or an integer scalar/vector.
    Y : Constant
        A set, or an integer scalar/vector.

        X and Y are of the same length.
    """
    ...


@builtin_function(_interval)
def interval(X: Constant, duration: Constant, fill: Constant, step: Constant = DFLT, explicitOffset: Constant = DFLT, closed: Constant = DFLT, label: Constant = DFLT, origin: Constant = DFLT) -> Constant:
    r"""In SQL queries, group data into continuous intervals with the length of
    duration. For intervals without any data, fill the results using the interpolation
    method specified by fill. This function must be used in a SQL group by clause.

    .. note::

        Temporal data types in "where" conditions are automatically converted.

    Parameters
    ----------
    X : Constant
        A vector of integral or temporal type.
    duration : Constant
        Of integral or duration type. The following time units are supported
        (case-sensitive): w, d, H, m, s, ms, us, ns, and trading calendar identifier
        consisting of four capital letters (the trading calendar file must be
        stored in marketHolidayDir). As time unit y is not supported, to group X
        by year, convert the data format of X with function year.
    fill : Constant
        Indicates how to fill the missing values of the result. It can take the
        value of "prev", "post", "linear", "null", a specific numeric value and "none".

        - "prev": the previous value

        - "post": the next value

        - "linear": linear interpolation. For non-numerical data, linear interpolation
          cannot be used and the "prev" method will be used instead.

        - "null": null value

        - a specific numeric value.

        - "none": do not interpolate
    step : Constant, optional
        Of integral or duration type. It's an optional parameter indicating the
        step size of the sliding window. It must be a number which can divide
        the duration. This parameter allows us to specify a sliding interval
        that is smaller than duration. The default value is the same as duration,
        which means the calculation window slides by the length of duration.

        .. note::

            If step is specified, the following aggregation calculations are not
            supported: atImax, atImin, difference, imax, imin, lastNot, mode, percentile.

            If the value of step differs from duration, user-defined aggregation
            functions are not supported for distributed queries.

    explicitOffset : Constant, optional
        An optional BOOLEAN. When explicitOffset = true, the first interpolation
        window starts at the starting point specified by the SQL where clause.
        When explicitOffset = false (default), the first interpolation window
        starts at the nearest point that is divisible by step before the starting
        point specified by the SQL where clause.
    closed : Constant, optional
        A string indicating which boundary of the interval is closed. It can be
        specified as 'left' or 'right'.
    label : Constant, optional
        A string indicating which boundary is used to label the interval with.
        It can be specified as 'left' or 'right'.
    origin : Constant, optional
        A string or a scalar of the same temporal type as X, indicating the timestamp
        when the intervals start. When origin is a string, it can be specified as:

        - 'epoch': 1970-01-01;

        - 'start': the first value of the timeseries;

        - 'start_day': 00:00 of the first day of the timeseries;

        - 'end': the last value of the timeseries;

        - 'end_day': 24:00 of the last day of the timeseries.

        Note that origin is specified only when explicitOffset = false.
    """
    ...


@builtin_function(_invBeta)
def invBeta(alpha: Constant, beta: Constant, p: Constant) -> Constant:
    r"""Return the value of a beta inverse cumulative distribution function.

    Parameters
    ----------
    alpha : Constant
        A positive floating number (shape parameter).
    beta : Constant
        A positive floating number (shape parameter).
    X : Constant
        A floating scalar or vector between 0 and 1.
    """
    ...


@builtin_function(_invBinomial)
def invBinomial(trials: Constant, prob: Constant, p: Constant) -> Constant:
    r"""Return the value of a binomial inverse cumulative distribution function.

    Parameters
    ----------
    trials : Constant
        A positive integer (shape parameter).
    p : Constant
        A floating number between 0 and 1 (shape parameter).
    X : Constant
        A floating scalar or vector between 0 and 1.
    """
    ...


@builtin_function(_invChiSquare)
def invChiSquare(df: Constant, p: Constant) -> Constant:
    r"""Return the value of a chi-squared inverse cumulative distribution function.

    Parameters
    ----------
    df : Constant
        A positive integer indicating the degree of freedom of a chi-squared distribution.
    X : Constant
        A floating scalar or vector between 0 and 1.
    """
    ...


@builtin_function(_invExp)
def invExp(mean: Constant, p: Constant) -> Constant:
    r"""Return the value of an exponential inverse cumulative distribution function.

    Parameters
    ----------
    mean : Constant
        The mean of an exponential distribution.
    X : Constant
        A floating scalar or vector between 0 and 1.
    """
    ...


@builtin_function(_invF)
def invF(numeratorDF: Constant, denominatorDF: Constant, p: Constant) -> Constant:
    r"""Return the value of an F inverse cumulative distribution function.

    Parameters
    ----------
    numeratorDF : Constant
        A positive integer indicating the degree of freedom of an F distribution.
    denominatorDF : Constant
        A positive integer indicating the degree of freedom of an F distribution.
    X : Constant
        A floating scalar or vector between 0 and 1.
    """
    ...


@builtin_function(_invGamma)
def invGamma(shape: Constant, scale: Constant, p: Constant) -> Constant:
    r"""Return the value of a gamma inverse cumulative distribution function.

    Parameters
    ----------
    shape : Constant
        A positive floating number (shape parameter).
    scale : Constant
        A positive floating number (scale parameter).
    X : Constant
        A floating scalar or vector between 0 and 1.
    """
    ...


@builtin_function(_invLogistic)
def invLogistic(mean: Constant, s: Constant, p: Constant) -> Constant:
    r"""Return the value of a logistic inverse cumulative distribution function.

    Parameters
    ----------
    mean : Constant
        The mean of a logistic distribution.
    s : Constant
        The scale parameter of a logistic distribution.
    X : Constant
        A floating scalar or vector between 0 and 1.
    """
    ...


@builtin_function(_invNormal)
def invNormal(mean: Constant, stdev: Constant, p: Constant) -> Constant:
    r"""Return the value of a normal inverse cumulative distribution function.

    Parameters
    ----------
    mean : Constant
        The mean of a normal distribution.
    stdev : Constant
        The standard deviation of a normal distribution.
    X : Constant
        A floating scalar or vector between 0 and 1.
    """
    ...


@builtin_function(_invPoisson)
def invPoisson(mean: Constant, p: Constant) -> Constant:
    r"""Return the value of a Poisson inverse cumulative distribution function.

    Parameters
    ----------
    mean : Constant
        The mean of a Poisson distribution.
    X : Constant
        A floating scalar or vector between 0 and 1.
    """
    ...


@builtin_function(_invStudent)
def invStudent(df: Constant, p: Constant) -> Constant:
    r"""Return the value of a Student's t inverse cumulative distribution function.

    Parameters
    ----------
    df : Constant
        A positive floating number indicating the degree of freedom of a Student's
        t-distribution.
    X : Constant
        A floating scalar or vector between 0 and 1.
    """
    ...


@builtin_function(_invUniform)
def invUniform(lower: Constant, upper: Constant, p: Constant) -> Constant:
    r"""Return the value of an uniform inverse cumulative distribution function.

    Parameters
    ----------
    lower : Constant
        A numeric scalar indicating the lower bound of a continuous uniform distribution.
    upper : Constant
        A numeric scalar indicating the upper bound of a continuous uniform distribution.
    X : Constant
        A floating scalar or vector between 0 and 1.
    """
    ...


@builtin_function(_invWeibull)
def invWeibull(alpha: Constant, beta: Constant, p: Constant) -> Constant:
    r"""Return the value of a Weibull inverse cumulative distribution function.

    Parameters
    ----------
    alpha : Constant
        A positive floating number (scale parameter).
    beta : Constant
        A positive floating number (shape parameter).
    X : Constant
        A floating scalar or vector between 0 and 1.
    """
    ...


@builtin_function(_inverse)
def inverse(obj: Constant) -> Constant:
    r"""Return the inverse matrix of X if it is invertible.

    Parameters
    ----------
    X : Constant
        A matrix.
    """
    ...


@builtin_function(_ipaddr)
def ipaddr(X: Constant) -> Constant:
    r"""Convert STRING into IPADDR (IP address) data type.

    Parameters
    ----------
    X : Constant
        A string scalar/vector.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_irs)
    def irs(settlement: Constant, resetInterval: Constant, start: Constant, maturity: Constant, notional: Constant, fixedRate: Constant, spread: Constant, curve: Constant, frequency: Constant, calendar: Constant, convention: Constant = DFLT, basis: Constant = DFLT, rateType: Constant = DFLT) -> Constant:
        r"""The irs function prices an interest rate swap (IRS) for the floating-rate side.

        An IRS is a derivative contract in which two parties agree to exchange one
        stream of interest payments for another over a set period of time. The most
        commonly traded IRS is the exchange of a fixed interest rate payment and a
        floating rate payment (typically benchmarked to an interbank offered rate LIBOR).

        .. note::

            Scalar inputs will be automatically expanded to match the length of other vector
            inputs. All vector inputs must be of equal length.

        Parameters
        ----------
        settlement : Constant
            A DATE scalar or vector indicating the settlement date.
        resetInterval : Constant
            A DURATION scalar or vector indicating how often the interest rate is reset.
        start : Constant
            A DATE scalar or vector indicating the start date.
        maturity : Constant
            A DATE scalar or vector indicating the maturity date.
        notional : Constant
            A numeric scalar or vector indicating the notional amount.
        fixedRate : Constant
            A numeric scalar or vector indicating the fixed rate(s).
        spread : Constant
            A numeric scalar or vector indicating the interest rate spread.
        curve : Constant
            A dictionary scalar or vector indicating the fitted yield curve.
        frequency : Constant
            An INT scalar/vector indicating the number of payments, or a STRING
            scalar/vector indicating payment frequency. It can be:

            - 0/"Once": Bullet payment at maturity.

            - 1/"Annual": Annual payments.

            - 2/"Semiannual": Semi-annual payments.

            - 4/"Quarterly": Quarterly payments.

            - 12/"Monthly": Monthly payments.
        calendar : Constant
            A STRING scalar or vector indicating the trading calendar(s). See Trading
            Calendar for more information.
        convention : Constant, optional
            A STRING scalar or vector indicating how cash flows that fall on a
            non-trading day are treated. The following options are available.
            Defaults to 'ModifiedFollowing'.

            - 'Following': The following trading day.

            - 'ModifiedFollowing': The following trading day. If that day is in a different month, the preceding trading day is adopted instead.

            - 'Preceding': The preceding trading day.

            - 'ModifiedPreceding': The preceding trading day. If that day is in a different month, the following trading day is adopted instead.

            - 'Unadjusted': Unadjusted.

            - 'HalfMonthModifiedFollowing': The following trading day. If that day crosses the mid-month (15th) or the end of month, the preceding trading day is adopted instead.

            - 'Nearest': The nearest trading day. If both the preceding and following trading days are equally far away, default to following trading day.
        rateType : Constant, optional
            An INT/STRING scalar or vector indicating compound interest. It can be:

            - 0/"CC" (default): continuous compounding

            - 1/"C": discrete compounding

        Returns
        -------
        Constant
            A DOUBLE scalar or vector.
        """
        ...


@builtin_function(_isAlNum)
def isAlNum(X: Constant) -> Constant:
    r"""Return "true" if all characters in string X are alphanumeric (either
    alphabets or numbers).

    If X is a table, the function is applied only to columns of character types
    (CHAR, STRING, or SYMBOL). Other column types are ignored.

    Parameters
    ----------
    X : Constant
        A CHAR/STRING/SYMBOL scalar, vector, or table.
    """
    ...


@builtin_function(_isAlpha)
def isAlpha(X: Constant) -> Constant:
    r"""Return "true" if all characters in the string are alphabets. For null
    values of the STRING type, return "false".

    Parameters
    ----------
    X : Constant
        A STRING scalar or vector.
    """
    ...


@builtin_function(_isDigit)
def isDigit(X: Constant) -> Constant:
    r"""Return "true" if all characters in the string are numbers. For null values
    of the STRING type, return "false".

    Parameters
    ----------
    X : Constant
        A STRING scalar or vector.
    """
    ...


@builtin_function(_isDuplicated)
def isDuplicated(X: Constant, keep: Constant = DFLT) -> Constant:
    r"""Return a vector or a tuple of vectors of Boolean values. If an element has
    no duplicate values, it returns 0.

    - If keep=FIRST, the first duplicate value returns 0 while all other duplicate
      values return 1.

    - If keep=LAST, the last duplicate value returns 0 while all other duplicate
      values return 1.

    - If keep=NONE, all duplicate values return 1.

    Parameters
    ----------
    X : Constant
        A vector or a tuple of vectors of same length.
    keep : Constant
        Can take the value of FIRST, LAST or NONE. It indicates how the system
        processes duplicate values. The default value is FIRST.
    """
    ...


@builtin_function(_isIndexedMatrix)
def isIndexedMatrix(X: Constant) -> Constant:
    r"""Determine if X is an indexed matrix.

    Parameters
    ----------
    X : Constant
        A matrix.
    """
    ...


@builtin_function(_isIndexedSeries)
def isIndexedSeries(X: Constant) -> Constant:
    r"""Determine if X is an indexed series.

    Parameters
    ----------
    X : Constant
        A matrix with only 1 column.
    """
    ...


@builtin_function(_isLeapYear)
def isLeapYear(X: Constant) -> Constant:
    r"""Determine if each element in X is in a leap year.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    """
    ...


@builtin_function(_isLower)
def isLower(X: Constant) -> Constant:
    r"""Check whether all the case-based characters (letters) of the string are lowercase.

    Parameters
    ----------
    X : Constant
        A STRING scalar or vector.
    """
    ...


@builtin_function(_isMonotonic)
def isMonotonic(X: Constant) -> Constant:
    r"""Alias for isMonotonicIncreasing. Check whether the elements in X are
    monotonically increasing.

    Parameters
    ----------
    X : Constant
        A scalar/vector.
    """
    ...


@builtin_function(_isMonotonicDecreasing)
def isMonotonicDecreasing(X: Constant) -> Constant:
    r"""Check whether the elements in X are monotonically decreasing.

    Parameters
    ----------
    X : Constant
        A scalar/vector.
    """
    ...


@builtin_function(_isMonotonicIncreasing)
def isMonotonicIncreasing(X: Constant) -> Constant:
    r"""Check whether the elements in X are monotonically increasing.

    Parameters
    ----------
    X : Constant
        A scalar/vector.
    """
    ...


@builtin_function(_isMonthEnd)
def isMonthEnd(X: Constant) -> Constant:
    r"""Determine if each element in X is the last day of a month.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    """
    ...


@builtin_function(_isMonthStart)
def isMonthStart(X: Constant) -> Constant:
    r"""Determine if each element in X is the first day of a month.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    """
    ...


@builtin_function(_isNanInf)
def isNanInf(X: Constant, includeNull: Constant = DFLT) -> Constant:
    r"""Check each element in X to see if it is a NaN/Inf value.

    Parameters
    ----------
    X : Constant
        A DOUBLE type scalar, vector or matrix.
    includeNull : Constant
        A BOOLEAN.

    Returns
    -------
    Constant
        A BOOLEAN type of the same length as X. If includeNull is set to true,
        null values will return true. The default value of includeNull is false.
    """
    ...


@builtin_function(_isNothing)
def isNothing(obj: Constant) -> Constant:
    r""""Nothing" is one of the two objects in VOID type.

    isNothing tests if a function argument is provided by the user.

    Parameters
    ----------
    X : Constant
        A scalar/vector.
    """
    ...


@builtin_function(_isNull)
def isNull(X: Constant) -> Constant:
    r"""Return true if an element is null.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix.
    """
    ...


@builtin_function(_isNumeric)
def isNumeric(X: Constant) -> Constant:
    r"""Return true if all characters in the string are numbers. For null values
    of the STRING type, return false.

    Parameters
    ----------
    X : Constant
        A STRING scalar or vector.
    """
    ...


@builtin_function(_isOrderedDict)
def isOrderedDict(X: Constant) -> Constant:
    r"""The function returns "true" if X is an ordered dictionary.

    Parameters
    ----------
    X : Constant
        A dictionary.
    """
    ...


@builtin_function(_isPeak)
def isPeak(X: Constant, strict: Constant = DFLT) -> Constant:
    r"""If X is a vector, check if each element in X is the peak.

    If X is a matrix, perform the aforementioned calculations on each column and
    return a matrix of the same size as X.

    If X is a table, only the numeric columns are involved in the calculations.

    Parameters
    ----------
    X : Constant
        A numeric vector/matrix/table.
    strict : Constant
        A Boolean value. For a segment of continuous identical numbers forming a
        local maximum (referred to as a plateau), the value of strict determines
        whether the entire plateau is considered a peak.

        - When strict = true, the plateau is not considered a peak, meaning all elements
          in the plateau return false.

        - When strict = false,

          - If the number of elements in plateau is odd, the element at the middle will
            return true, while the others return false.

          - If even, the element on the left side of the two middle elements will return
            true, while the others return false.
    """
    ...


@builtin_function(_isQuarterEnd)
def isQuarterEnd(X: Constant) -> Constant:
    r"""Determine if each element in X is the last day of a quarter.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    """
    ...


@builtin_function(_isQuarterStart)
def isQuarterStart(X: Constant) -> Constant:
    r"""Determine if each element in X is the first day of a quarter.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    """
    ...


@builtin_function(_isSorted)
def isSorted(X: Constant, ascending: Constant = DFLT) -> Constant:
    r"""Check whether a vector is sorted or not.

    Parameters
    ----------
    X : Constant
        A vector.
    ascending : Constant
        A Boolean indicating whether X is sorted in ascending order(true) or
        descending order(false). The default value is true.
    """
    ...


@builtin_function(_isSpace)
def isSpace(X: Constant) -> Constant:
    r"""Check whether the string X consists of only space. Return "true" if all characters in X
    are space, ``\t`` (tab), ``\r`` (carriage return) or ``\n`` (newline escape).

    Parameters
    ----------
    X : Constant
        A STRING scalar or vector.
    """
    ...


@builtin_function(_isTitle)
def isTitle(X: Constant) -> Constant:
    r"""Check if X is a titlecased string, which has the first character in each
    word uppercase and the remaining all characters lowercase alphabets.

    Parameters
    ----------
    X : Constant
        A STRING scalar or vector.
    """
    ...


@builtin_function(_isUpper)
def isUpper(X: Constant) -> Constant:
    r"""Check whether all the case-based characters (letters) of the string are uppercase.

    Parameters
    ----------
    X : Constant
        A STRING scalar or vector.
    """
    ...


@builtin_function(_isValid)
def isValid(X: Constant) -> Constant:
    r"""Determine if each element of X is null. Return true if at least one element
    is not null and false otherwise.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix.
    """
    ...


@builtin_function(_isValley)
def isValley(X: Constant, strict: Constant = DFLT) -> Constant:
    r"""If X is a vector, check if each element in X is the valley.

    If X is a matrix, perform the aforementioned calculations on each column and
    return a matrix of the same size as X.

    If X is a table, only the numeric columns are involved in the calculations.

    Parameters
    ----------
    X : Constant
        A numeric vector/matrix/table.
    strict : Constant
        A Boolean value. For a segment of continuous identical numbers forming a
        local maximum (referred to as a plateau), the value of strict determines
        whether the entire plateau is considered a valley.

        - When strict = true, the plateau is not considered a valley, meaning all elements
          in the plateau return false.

        - When strict = false,

          - If the number of elements in plateau is odd, the element at the middle will
            return true, while the others return false.

          - If even, the element on the left side of the two middle elements will return
            true, while the others return false.
    """
    ...


@builtin_function(_isVoid)
def isVoid(obj: Constant) -> Constant:
    r"""Check if an object is VOID type. There are two types of objects with VOID
    type: NULL object and Nothing object. Please see isNothing.

    Parameters
    ----------
    X : Constant
        Can be of any data form.
    """
    ...


@builtin_function(_isYearEnd)
def isYearEnd(X: Constant) -> Constant:
    r"""Determine if each element in X is the last day of a year.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    """
    ...


@builtin_function(_isYearStart)
def isYearStart(X: Constant) -> Constant:
    r"""Determine if each element in X is the first day of a year.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    """
    ...


@builtin_function(_isort)
def isort(X: Constant, ascending: Constant = DFLT) -> Constant:
    r"""Instead of returning a sorted vector like sort_, isort returns the indexes
    in the original vector for each element in the sorted vector.

    `X[F.isort(X)]` is equivalent to `sort_(X)`.

    Parameters
    ----------
    X : Constant
        A vector or a tuple of vectors of the same length.
    ascending : Constant
        A Boolean scalar or vector indicating whether to sort X (or vectors of X
        sequentially) in ascending order or descending order. The default value
        is true (ascending order).
    """
    ...


@builtin_function(_isort_)
def isort_(X: Constant, ascending: Constant, indices: Constant) -> Constant:
    r"""`isort_(x, ascending, y)` is equivalent to `y[F.isort(x, ascending)]`. The result
    is assigned to y.

    Parameters
    ----------
    X : Constant
        A vector or a tuple of vectors of the same length.
    ascending : Constant
        A Boolean scalar indicating whether to sort X (or vectors of X sequentially)
        in ascending order or descending order. The default value is true (ascending
        order).
    indices : Constant
        A vector of the same length as each vector in X.
    """
    ...


@builtin_function(_isortTop)
def isortTop(X: Constant, top: Constant, ascending: Constant = DFLT) -> Constant:
    r"""Return the first few elements of the result of isort(X, [ascending]).

    Parameters
    ----------
    X : Constant
        A vector or a tuple of vectors of the same length.
    top : Constant
        A positive integer no more than the size of a vector in X.
    ascending : Constant
        A Boolean scalar or vector indicating whether to sort X (or vectors of X
        sequentially) in ascending order or descending order. The default value
        is true (ascending order).
    """
    ...


@builtin_function(_iterate)
def iterate(init: Constant, coeffs: Constant, input: Constant) -> Constant:
    r"""If init, coeffs and input are all scalars, return a geometric sequence
    [init*coeffs, init*coeffs^2, init*coeffs^3, …]. The length of the sequence
    is input.

    If init and coeffs are scalars and input is a vector, return an array x with
    x[0]=init*coeffs + input[0] and x[n]=x[n-1]* coeffs + input[n].

    If init and coeffs are vectors and input is a scalar, return an array x with
    x[n]=y(n)** coeffs, y(n)=y(n-1)[1:].append_(x[n-1]), y(0)= init. The length
    of x is input. ** returns the inner product of 2 vectors.

    If init, coeffs and input are all vectors, return an array x with x[n]=y(n)**
    coeffs + input[n], y(n)=y(n-1)[1:].append_(x[n-1]), y(0)= init. The length of
    x is input. ** returns the inner product of 2 vectors.

    Parameters
    ----------
    init : Constant
        A scalar or a vector.
    coeffs : Constant
        A scalar or a vector. init and coeffs have the same length.
    input : Constant
        A scalar or a vector. If input is a scalar, it must be an integer and it
        means the number of iterations; if input is a vector, its length means
        the number of iterations and each element of input is added to the result
        of the corresponding iteration.
    """
    ...


@builtin_function(_join)
def join(obj1: Constant, obj2: Constant) -> Constant:
    r"""Merge X and Y.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    Y : Constant
        A scalar/vector/matrix/table.

    Returns
    -------
    Constant
        If X is a scalar, Y can be a scalar/vector. The result is a vector.

        If X is a vector, Y must be a scalar/vector. The result is a vector.

        If X is a matrix, Y must be a vector/matrix with the same number of rows as X.
        The result is a matrix with the same number of rows as X.

        If X is a table, Y must be a table or a vector with the same number of rows as X.
        The result is a table with the same number of rows as X.
    """
    ...


@builtin_function(_join_)
def join_(obj: Constant, newData: Constant) -> Constant:
    r"""Merge X and Y, and assign the result to X. The resulting object has the same data type as X.

    Parameters
    ----------
    X : Constant
        A vector/tuple/matrix/table.
    Y : Constant
        A scalar/vector/tuple/matrix/table.

        If X is a vector, Y is a scalar/vector/tuple; if X is a matrix, Y is a vector/matrix;
        if X is a table, Y is a vector/table.
    """
    ...


@builtin_function(_jsonExtract)
def jsonExtract(json: Constant, location: Constant, type: Constant) -> Constant:
    r"""This function parses extracted JSON elements into specified data type.

    Parameters
    ----------
    json : Constant
        A LITERAL scalar or vector indicating the standard JSON string(s) to parse.
    location : Constant
        A scalar/vector/tuple. Each element can be a string or a non-zero integer indicating
        the location at the corresponding dimension.

        - String: access element by key.

        - Positive integer: access the n-th element from the beginning.

        - Negative integer: access the n-th element from the end.
    type : Constant
        A string specifying the data type of the return value. It can be "long", "int",
        "double", or "string".

    Returns
    -------
    Constant
        If json is a scalar, it returns a scalar; If json is a vector, it returns a vector.

        If an element corresponding to location does not exist or cannot be parsed into expected
        data type, NULL is returned.
    """
    ...


@builtin_function(_kama)
def kama(X: Constant, window: Constant) -> Constant:
    r"""Calculate the Kaufman Adaptive Moving Average for X with a rolling window.
    The length of the window is given by the parameter window. The result is of the same
    length as X. The first (window-1) elements of the result are null values.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    window : Constant
        A positive integer indicating the size of the sliding window.
    """
    ...


@builtin_function(_kendall)
def kendall(X: Constant, Y: Constant) -> Constant:
    r"""Calculate the Kendall rank correlation coefficient between X and Y. Null values
    are ignored in the calculation.

    If X or Y is a matrix, perform the aforementioned calculation on each column and
    return a vector.

    If X or Y is an in-memory table, perform the aforementioned calculation on each
    numeric column of the table and return a table (where null values are returned for
    non-numeric columns).

    Parameters
    ----------
    X : Constant
        A scalar, vector, matrix or in-memory table.
    Y : Constant
        A scalar, vector, matrix or in-memory table.
    """
    ...


@builtin_function(_keyedStreamTable)
def keyedStreamTable(*args) -> Constant:
    r"""This function creates a stream table with one or more columns serving as the
    primary key. It implements idempotent writes to prevent duplicate primary key
    insertions due to network issues or high-availability writes.

    When new records are inserted into a keyed stream table, the system checks the
    values of primary key.

    - If the primary key of a new record is identical to an existing one in memory,
      the new record is not inserted, and the existing record remains unchanged.

    - If multiple new records with the same primary key (different from those in
      memory) are written simultaneously, only the first record is successfully inserted.

    .. note::

        The uniqueness of the primary key is limited to data in memory. If persistence
        is enabled for the keyed stream table, a limited number of records are stored in
        memory, with older data being persisted to disk. The primary key of incoming data
        could potentially duplicate those on disk.
    """
    ...


@builtin_function(_keyedTable)
def keyedTable(*args) -> Constant:
    r"""Create an keyed table, which is a special type of in-memory table with primary
    key. The primary key can be one column or multiple columns. The keyed table is
    implemented based on a hash table, storing the combined value of the primary key
    fields as a key entry, with each key entry corresponding to a record in the table.
    During queries, by specifying all fields of the primary key, data can be located
    through the index without performing a full table scan. It is recommended to use
    sliceByKey to improve query performance.

    When adding new records to the table, if the primary key of the new record duplicates
    an existing record, the system updates the record in the table; otherwise, the
    new record is added to the table.

    Keyed tables exhibit better performance for single-record updates and queries,
    making them an ideal choice for data caching. Keyed tables can also serve as output
    tables for time series engines for real time updates.

    .. note::

        This function does not support creating a keyed table containing array vector columns.
    """
    ...


@builtin_function(_keys)
def keys(obj: Constant) -> Constant:
    r"""Return the keys of a dictionary as a vector, or return the column names of a
    table as a vector, or convert a set into a vector.

    Parameters
    ----------
    X : Constant
        A dictionary/table/set.
    """
    ...


@builtin_function(_kmeans)
def kmeans(X: Constant, k: Constant, maxIter: Constant = DFLT, randomSeed: Constant = DFLT, init: Constant = DFLT) -> Constant:
    r"""K-means clustering.

    Parameters
    ----------
    X : Constant
        A table. Each row is an observation and each column is a feature.
    k : Constant
        A positive integer indicating the number of clusters to form.
    maxIter : Constant
        A positive integer indicating the maximum number of iterations of the k-means
        algorithm for a single run. The default value is 300.
    randomSeed : Constant
        An integer indicating the seed in the random number generator.
    init : Constant
        A STRING scalar or matrix indicating the optional method for initialization.
        The default value is "random".

        - If init is a STRING scalar, it can be "random" or "k-means++": "random"
          means to choose observations at random from data for the initial centroids;
          "k-means++" means to generate cluster centroids using the k-means++ algorithm.

        - If init is a matrix, it indicates the centroid starting locations. The
          number of columns is the same as X and the number of rows is k.

    Returns
    -------
    Constant
        A dictionary with the following keys:

        - centers: a k*m (m is the number of columns of X) matrix. Each row is the
          coordinates of a cluster center.

        - predict: a clustering function for prediction of FUNCTIONDEF type.

        - modelName: string "KMeans".

        - model: a RESOURCE data type variable. It is an internal binary resource
          generated by function kmeans to be used by function predict.

        - labels: a vector indicating which cluster each row of X belongs to.
    """
    ...


@builtin_function(_knn)
def knn(Y: Constant, X: Constant, type: Constant, nNeighbor: Constant, power: Constant = DFLT) -> Constant:
    r"""Implement the k-nearest neighbors (k-NN) algorithm with a brute-force search
    for classification and regression.

    Parameters
    ----------
    Y : Constant
        A vector with the same length as the number of rows of X. Each element is a
        label corresponding to each row in X.
    X : Constant
        A table. Each row is an observation and each column is a feature.
    type : Constant
        A string. It can be either "regressor" or "classifier".
    nNeighbor : Constant
        A positive integer indicating the number of nearest neighbors in training.
    power : Constant
        A positive integer indicating the parameter of Minkowski distance used in
        training. The default value is 2 indicating Euclidean distance. If power=1,
        it means Manhattan distance is used in training.

    Returns
    -------
    Constant
        A dictionary with the following keys:

        - nNeighbor: the number of nearest neighbors in training.

        - modelName: string "KNN".

        - model: the model to be saved.

        - power: the parameter of Minkowski distance used in training.

        - type: "regressor" or "classifier".
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_kroghInterpolate)
    def kroghInterpolate(X: Constant, Y: Constant, newX: Constant, der: Constant = DFLT) -> Constant:
        r"""Interpolating polynomial for a set of points. The polynomial passes through
        all the pairs (X, Y) and returns the derivative interpolated at the x-points.

        One may additionally specify a number of derivatives at each point Xi; this is done
        by repeating the value Xi and specifying the derivatives as successive Yi values.

        - When the vector of Xi contains only distinct values, Yi represents the function value.

        - When an element of Xi occurs two or more times in a row, the corresponding Yi represents
          derivative values. For example, if X = [0,0,1,1] and Y = [1,0,2,3], then Y[0]=f(0),
          Y[1]=f'(0), Y[2]=f(1) and Y[3]=f'(1).

        Parameters
        ----------
        X : Constant
            A numeric vector indicating the x-coordinates. It must be sorted in increasing
            order with no null values contained.
        Y : Constant
            A numeric vector of the same length as Xi, indicating the y-coordinates. It
            cannot contain null values.
        newX : Constant
            A numeric vector specifying the points at which to evaluate the derivatives.
        der : Constant, optional
            A non-negative integer indicating how many derivatives to evaluate. The default
            value is 0, meaning the function value is used as the 0th derivative.
        """
        ...


if not sw_is_ce_edition():
    @builtin_function(_kroghInterpolateFit)
    def kroghInterpolateFit(X: Constant, Y: Constant, der: Constant = DFLT) -> Constant:
        r"""This function performs polynomial interpolation for a given set of points,
        ensuring the polynomial passes through all points in the set.

        Multiple derivative values at each point of X can be specified by repeating X
        values and assigning corresponding derivative values as consecutive Y values:

        - If an X value appears only once, the corresponding Y is the value of the polynomial f(X).

        - If an X value appears multiple times, the first Y is the value of f(X), the second Y
          is the first derivative f'(X), the third Y is the second derivative f''(X), and so on.
          For example, with inputs X=[0,0,1,1] and Y=[1,0,2,3], the interpretation is Y[0]=f(0),
          Y[1]=f'(0), Y[2]=f(1), Y[3]=f'(1).

        Parameters
        ----------
        X : Constant
            A a numeric vector representing the x-coordinates of the points to be interpolated.
            Values in X must be in increasing order. Null values are not allowed.
        Y : Constant
            A numeric vector of the same length as X, representing the y-coordinates of
            the points. Null values are not allowed.
        der : Constant, optional
            A non-negative integer representing the derivative order to compute. The default
            value is 0, meaning to compute the polynomial's value.

        Returns
        -------
        Constant
            A dictionary with the following keys:

            - modelName: A string "kroghInterpolate" indicating the model name.

            - X: The numeric vector representing the x-coordinates used for interpolation
              (i.e., the input X).

            - der: The non-negative integer representing the derivative order (i.e., the input der).

            - coeffs: A numeric vector containing the polynomial coefficients fitted from the
              input data points.

            - predict: The prediction function of the model. You can call model.predict(X) or
              predict(model, X) to make predictions with the generated model. It takes the
              following parameters:

            - model: A dictionary, which is the output of kroghInterpolateFit.

            - X: A numeric vector representing the x-coordinates at which to evaluate the polynomial.
        """
        ...


@builtin_function(_ksTest)
def ksTest(X: Constant, Y: Constant) -> Constant:
    r"""Conduct Kolmogorov-Smirnov test on X and Y.

    - ksValue: Kolmogorov-Smirnov statistic

    - pValue: p-value of the test

    - D: D-stat

    - method: "Two-sample Kolmogorov-Smirnov test"

    Parameters
    ----------
    X : Constant
        A numeric vector indicating the sample for the test.
    Y : Constant
        A numeric vector indicating the sample for the test.
    """
    ...


@builtin_function(_kurtosis)
def kurtosis(X: Constant, biased: Constant = DFLT) -> Constant:
    r"""Return the kurtosis of X. The calculation skips null values.

    Parameters
    ----------
    X : Constant
        A vector/matrix.
    biased : Constant
        A Boolean value indicating whether the result is biased. The default value is
        true, meaning the bias is not corrected.
    """
    ...


@builtin_function(_lasso)
def lasso(ds: Constant, yColName: Constant, xColNames: Constant, alpha: Constant = DFLT, intercept: Constant = DFLT, normalize: Constant = DFLT, maxIter: Constant = DFLT, tolerance: Constant = DFLT, positive: Constant = DFLT, swColName: Constant = DFLT, checkInput: Constant = DFLT) -> Constant:
    r"""Estimate a Lasso regression that performs L1 regularization.

    Parameters
    ----------
    ds : Constant
        An in-memory table or a data source usually generated by the sqlDS function.
    yColName : Constant
        A string indicating the column name of the dependent variable in ds.
    xColNames : Constant
        A string scalar/vector indicating the column names of the independent variables
        in ds.
    alpha : Constant
        A floating number representing the constant that multiplies the L1-norm. The
        default value is 1.0.
    intercept : Constant
        A Boolean value indicating whether to include the intercept in the regression.
        The default value is true.
    normalize : Constant
        A Boolean value. If true, the regressors will be normalized before regression
        by subtracting the mean and dividing by the L2-norm. If intercept =false, this
        parameter will be ignored. The default value is false.
    maxIter : Constant
        A positive integer indicating the maximum number of iterations. The default
        value is 1000.
    tolerance : Constant
        A floating number. The iterations stop when the improvement in the objective
        function value is smaller than tolerance. The default value is 0.0001.
    positive : Constant
        A Boolean value indicating whether to force the coefficient estimates to be
        positive. The default value is false.
    swColName : Constant
        A STRING indicating a column name of ds. The specified column is used as the
        sample weight. If it is not specified, the sample weight is treated as 1.
    checkInput : Constant
        A BOOLEAN value. It determines whether to enable validation check for parameters
        yColName, xColNames, and swColName.

        - If checkInput = true (default), it will check the invalid value for parameters
          and throw an error if the null value exists.

        - If checkInput = false, the invalid value is not checked.

        It is recommended to specify checkInput = true. If it is false, it must be ensured
        that there are no invalid values in the input parameters and no invalid values
        are generated during intermediate calculations, otherwise the returned model may
        be inaccurate.
    """
    ...


@builtin_function(_lassoBasic)
def lassoBasic(Y: Constant, X: Constant, mode: Constant = DFLT, alpha: Constant = DFLT, intercept: Constant = DFLT, normalize: Constant = DFLT, maxIter: Constant = DFLT, tolerance: Constant = DFLT, positive: Constant = DFLT, swColName: Constant = DFLT, checkInput: Constant = DFLT) -> Constant:
    r"""Perform lasso regression.

    Parameters
    ----------
    Y : Constant
        A numeric vector indicating the dependent variables.
    X : Constant
        A numeric vector/tuple/matrix/table, indicating the independent variables.

        - When X is a vector/tuple, its length must be equal to the length of Y.

        - When X is a matrix/table, its number of rows must be equal to the length
          of Y.
    mode : Constant
        An integer that can take the following three values:

        - 0 (default) : a vector of the coefficient estimates.

        - 1: a table with coefficient estimates, standard error, t-statistics, and
          p-values.

        - 2: a dictionary with the following keys: ANOVA, RegressionStat, Coefficient
          and Residual.
    alpha : Constant
        A floating number representing the constant that multiplies the L1-norm. The
        default value is 1.0.
    intercept : Constant
        A Boolean variable indicating whether the regression includes the intercept.
        If it is true, the system automatically adds a column of "1"s to X to generate
        the intercept. The default value is true.
    normalize : Constant
        A Boolean value. If true, the regressors will be normalized before regression
        by subtracting the mean and dividing by the L2-norm. If intercept =false, this
        parameter will be ignored. The default value is false.
    maxIter : Constant
        A positive integer indicating the maximum number of iterations. The default
        value is 1000.
    tolerance : Constant
        A floating number. The iterations stop when the improvement in the objective
        function value is smaller than tolerance. The default value is 0.0001.
    positive : Constant
        A Boolean value indicating whether to force the coefficient estimates to be
        positive. The default value is false.
    swColName : Constant
        A STRING indicating a column name of ds. The specified column is used as the
        sample weight. If it is not specified, the sample weight is treated as 1.
    checkInput : Constant
        A BOOLEAN value. It determines whether to enable validation check for parameters
        yColName, xColNames, and swColName.

        - If checkInput = true (default), it will check the invalid value for parameters
          and throw an error if the null value exists.

        - If checkInput = false, the invalid value is not checked.

        .. note::

            It is recommended to specify checkInput = true. If it is false, it must be
            ensured that there are no invalid values in the input parameters and no
            invalid values are generated during intermediate calculations, otherwise
            the returned model may be inaccurate.
    """
    ...


@builtin_function(_lassoCV)
def lassoCV(ds: Constant, yColName: Constant, xColNames: Constant, alphas: Constant = DFLT, intercept: Constant = DFLT, normalize: Constant = DFLT, maxIter: Constant = DFLT, tolerance: Constant = DFLT, positive: Constant = DFLT, swColName: Constant = DFLT, checkInput: Constant = DFLT) -> Constant:
    r"""Estimate a Lasso regression using 5-fold cross-validation and return a model
    corresponding to the optimal parameters.

    Parameters
    ----------
    ds : Constant
        An in-memory table or a data source usually generated by the sqlDS function.
    yColName : Constant
        A string indicating the column name of the dependent variable in ds.
    xColNames : Constant
        A string scalar/vector indicating the column names of the independent variables
        in ds.
    alphas : Constant, optional
        A floating-point scalar or vector that represents the coefficient multiplied
        by the L1 norm penalty term. The default value is [0.01, 0.1, 1.0].
    intercept : Constant
        A Boolean value indicating whether to include the intercept in the regression.
        The default value is true.
    normalize : Constant
        A Boolean value. If true, the regressors will be normalized before regression
        by subtracting the mean and dividing by the L2-norm. If intercept =false, this
        parameter will be ignored. The default value is false.
    maxIter : Constant
        A positive integer indicating the maximum number of iterations. The default
        value is 1000.
    tolerance : Constant
        A floating number. The iterations stop when the improvement in the objective
        function value is smaller than tolerance. The default value is 0.0001.
    positive : Constant
        A Boolean value indicating whether to force the coefficient estimates to be
        positive. The default value is false.
    swColName : Constant
        A STRING indicating a column name of ds. The specified column is used as the
        sample weight. If it is not specified, the sample weight is treated as 1.
    checkInput : Constant
        A BOOLEAN value. It determines whether to enable validation check for parameters
        yColName, xColNames, and swColName.

        - If checkInput = true (default), it will check the invalid value for parameters
          and throw an error if the null value exists.

        - If checkInput = false, the invalid value is not checked.

        It is recommended to specify checkInput = true. If it is false, it must be ensured
        that there are no invalid values in the input parameters and no invalid values
        are generated during intermediate calculations, otherwise the returned model may
        be inaccurate.

    Returns
    -------
    Constant
        A dictionary containing the following keys

        - modelName: the model name, which is "LassoCV" for this method

        - coefficients: the regression coefficients

        - intercept: the intercept

        - dual_gap: the dual gap

        - tolerance: the tolerance for the optimization

        - iterations: the number of iterations

        - xColNames: the column names of the independent variables in the data source

        - predict: the function used for prediction

        - alpha: the penalty term for cross-validation
    """
    ...


@builtin_function(_last)
def last(X: Constant) -> Constant:
    r"""Return the last element of a vector, or the last row of a matrix or table.

    If the last element is null, the function returns NULL. To get the last non-null
    element, use lastNot.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_lastNot)
def lastNot(X: Constant, k: Constant = DFLT) -> Constant:
    r"""If X is a vector:

    - If k is not specified: return the last element of X that is not null.

    - If k is specified: return the last element of X that is neither k nor null.

    If X is a matrix/table, conduct the aforementioned calculation within each column
    of X. The result is a vector.

    lastNot also supports querying DFS tables and partitioned tables.

    Parameters
    ----------
    X : Constant
        A vector, a matrix or a table.
    k : Constant, optional
        A scalar.
    """
    ...


@builtin_function(_lastWeekOfMonth)
def lastWeekOfMonth(X: Constant, weekday: Constant = DFLT, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""In the calendar month of X, suppose the last "weekday" is d.

    - If X <d: return the last "weekday" in the previous calendar month.

    - If X >=d: return the last "weekday" in the current calendar month.

    If parameter offset is specified, the result is updated every n months. Parameter
    offset works only if parameter n >1.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type DATE, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    weekday : Constant
        An integer from 0 to 6. 0 means Monday, 1 means Tuesday, ..., and 6 means Sunday.
        The default value is 0.
    offset : Constant
        A scalar of the same data type as X. It must be no greater than the minimum
        value of X. The default value is the minimum value of X.
    n : Constant
        A positive integer. The default value is 1.
    """
    ...


@builtin_function(_latestIndexedTable)
def latestIndexedTable(*args) -> Constant:
    r"""Create an indexed table, which is a special type of in-memory table with primary
    key. The primary key can be one column or multiple columns. Compared to the indexedTable,
    latestIndexedTable adds a time column to determine whether to update records.

    When a new record is appended to the indexed table, if its timestamp is smaller
    than that of the existing row which has the same primary key, it does not overwrite
    the existing row. latestIndexedTable deduplicates records with the same primary
    key based on the time column, which affects its writing performance (relatively
    slow compared with indexedTable).

    .. note::

        The primary key cannot be updated.

        Refer to indexedTable for the optimization of query performance on latestIndexedTable.
    """
    ...


@builtin_function(_latestKeyedStreamTable)
def latestKeyedStreamTable(*args) -> Constant:
    r"""Create a keyed stream table with one or more columns serving as the primary key.
    Compared to the keyedStreamTable, latestKeyedStreamTablemaintains the most up-to-date
    record for each unique primary key based on a time column. When a new record arrives,
    the system compares its primary key to existing records in memory:

    - If a match is found, check the timestamps:

      - If the new record's timestamp is more recent, it is inserted and replace the
        existing record.

      - If not, the existing record remains unchanged.

    - If no matching primary key is found, add the new record to the table. In cases
      where multiple new records with the same key are written simultaneously, only
      the record with the most recent timestamp is inserted.
    """
    ...


@builtin_function(_latestKeyedTable)
def latestKeyedTable(*args) -> Constant:
    r"""Create a keyed table, which is a special type of in-memory table with primary
    key. The primary key can be one column or multiple columns. Compared to the keyedTable,
    latestKeyedTable adds a time column to determine whether to update records.

    When a new record is appended to the keyed table, if its timestamp is smaller than
    that of the existing row which has the same primary key, it does not overwrite the
    existing row. latestKeyedTable deduplicates records with the same primary key based
    on the time column, which affects its writing performance (relatively slow compared
    with keyedTable).

    .. note::

        The primary key cannot be modified (with functions update, or replaceColumn_)
        or deleted (with functions alter, or dropColumns_).
    """
    ...


@builtin_function(_le)
def le(X: Constant, Y: Constant) -> Constant:
    r"""If neither X nor Y is a set, return the element-by-element comparison of X<=Y.

    If both X and Y are sets, check if X is a subset of Y.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix/set.
    Y : Constant
        A scalar/pair/vector/matrix/set. If X or Y is a pair/vector/matrix, the other
        is a scalar or a pair/vector/matrix of the same size.
    """
    ...


@builtin_function(_left)
def left(X: Constant, n: Constant) -> Constant:
    r"""Return the first n characters of string X.

    If X is a table, the function is applied only to columns of STRING type. Other
    column types are ignored.

    Parameters
    ----------
    X : Constant
        A STRING scalar/vector, or table.
    n : Constant
        A positive integer.
    """
    ...


@builtin_function(_lfill)
def lfill(obj: Constant) -> Constant:
    r"""If obj is a vector: linearly fill the null values between 2 non-null numeric
    values in obj.

    If obj is a table with only numeric columns: for each column of the table, linearly
    fill the null values between 2 non-null numeric values.

    lfill does not change obj, whereas lfill_ changes obj.

    Parameters
    ----------
    obj : Constant
        A vector or a table with only numeric columns.
    """
    ...


@builtin_function(_lfill_)
def lfill_(obj: Constant) -> Constant:
    r"""If obj is a vector: linearly fill the null values between 2 non-null numeric
    values in obj.

    If obj is a table with only numeric columns: for each column of the table, linearly
    fill the null values between 2 non-null numeric values.

    The only difference between lfill and lfill_ is that the latter assigns the result
    to X and thus changing the value of X after the execution.

    Parameters
    ----------
    obj : Constant
        A vector or a table with only numeric columns.
    """
    ...


@builtin_function(_license)
def license(fileName: Constant = DFLT, pubKeyFile: Constant = DFLT, read: Constant = DFLT) -> Constant:
    r"""Display information regarding the DolphinDB license. If fileName is not specified,
    the license information from memory is obtained by default.

    Parameters
    ----------
    fileName : Constant, optional
        The path of the license.
    pubKeyFile : Constant, optional
        The path of the public key file.
    read : Constant, optional
        A Boolean value indicating whether to disable the license file verification
        before returning the result. The default value is false.

    Returns
    -------
    Constant
        A dictionary with the following keys:

        +----------------+-------------------------------------------------------------------------------------------------------------------------+
        | Keys           | Meaning                                                                                                                 |
        +================+=========================================================================================================================+
        | authorization  | authorization types: trial/test/commercial                                                                              |
        +----------------+-------------------------------------------------------------------------------------------------------------------------+
        | licenseType    | The license type:                                                                                                       |
        |                | 1: fingerprint authentication;                                                                                          |
        |                | 2: online verification;                                                                                                 |
        |                | 3: license server;                                                                                                      |
        |                | 0: others                                                                                                               |
        +----------------+-------------------------------------------------------------------------------------------------------------------------+
        | maxMemoryPerNode | the maximum memory for each node (in GB)                                                                              |
        +----------------+-------------------------------------------------------------------------------------------------------------------------+
        | bindCores      | CPU ID(s) (starting from 0) that are already bound to the DolphinDB process.                                            |
        |                | Note that it takes effect only when bindCPU is configured to true.                                                      |
        +----------------+-------------------------------------------------------------------------------------------------------------------------+
        | maxCoresPerNode | the maximum cores for each node                                                                                        |
        +----------------+-------------------------------------------------------------------------------------------------------------------------+
        | clientName     | the client name                                                                                                         |
        +----------------+-------------------------------------------------------------------------------------------------------------------------+
        | port           | the port number bound to the node. It is returned only for the license server and its connected nodes.                  |
        +----------------+-------------------------------------------------------------------------------------------------------------------------+
        | bindCPU        | whether a DolphinDB process is bound to a CPU                                                                           |
        +----------------+-------------------------------------------------------------------------------------------------------------------------+
        | expiration     | the expiration date of the license                                                                                      |
        +----------------+-------------------------------------------------------------------------------------------------------------------------+
        | maxNodes       | the maximum number of nodes for the cluster                                                                             |
        +----------------+-------------------------------------------------------------------------------------------------------------------------+
        | version        | the version number of the server. Only a server that is not higher than the version can be used.                        |
        |                | If it is empty, there is no restriction on the version.                                                                 |
        +----------------+-------------------------------------------------------------------------------------------------------------------------+
        | modules        | a decimal converted from 4-bit binary number, indicating the supported modules.                                         |
        +----------------+-------------------------------------------------------------------------------------------------------------------------+
        | moduleNames    | names of supported modules. Currently, only orderbook, internalFunction, cep, gpu, starfish, Beluga,                    |
        |                | Backtest, MatchingEngineSimulator will be returned.                                                                     |
        +----------------+-------------------------------------------------------------------------------------------------------------------------+
        | productKey     | the current product. The return value includes DOLPHIN, IOTBASIC, IOTPRO, SHARK, SWORDFISH, ORCA, DOLPHINX.             |
        +----------------+-------------------------------------------------------------------------------------------------------------------------+
    """
    ...


@builtin_function(_like)
def like(X: Constant, pattern: Constant) -> Constant:
    r"""Return a Boolean value scalar or vector indicating whether each element in X
    fits a specific pattern. The comparison is case sensitive.

    Parameters
    ----------
    X : Constant
        A STRING scalar/vector.
    pattern : Constant
        A string and is usually used with a wildcard character such as %.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_linearInterpolateFit)
    def linearInterpolateFit(X: Constant, Y: Constant, fillValue: Constant = DFLT, sorted: Constant = DFLT) -> Constant:
        r"""Perform linear interpolation/extrapolation on a set of points. Interpolation
        estimates unknown values that fall between known data points, while extrapolation
        estimates values beyond the existing data range.

        Parameters
        ----------
        X : Constant
            A numeric vector indicating the x-coordinates of the points for interpolation.
            Note that X must contain no less than two unique values with no null values.
        Y : Constant
            A numeric vector indicating the y-coordinates of the points for interpolation.
            Note that Y must be of the same length as X with no null values.
        fillValue : Constant, optional
            Specifies how to assign values for the x-coordinate of the points outside
            the existing data range. The following options are supported:

            - A numeric pair in the form (min, max), where min and max represent the
              values assigned when the x-coordinate of the point Xnew is smaller than
              the minimum of X or larger than the maximum of X, respectively. Specifically:

              - If Xnew < Xmin, it is assigned below.

              - If Xnew > Xmax, it is assigned above.

            - The string "extrapolate" (default), which indicates that extrapolation
              is performed.
        sorted : Constant, optional
            A Boolean scalar indicating whether the input X is sorted in ascending order.

            - If set to true, X must be in ascending order.

            - If set to false (default), the function will sort X and adjust the order
              of Y accordingly.

        Returns
        -------
        Constant
            A dictionary containing the following keys:

            - modelName: A string indicating the model name, which is "linearInterpolate".

            - sortedX: A DOUBLE vector indicating the input Xsorted in ascending order.

            - sortedY: A DOUBLE vector indicating the input Y sorted corresponding to
              sortedX.

            - fillValue: The input fillValue.

            - predict: The prediction function of the model, which returns linear interpolation
              results. It can be called using model.predict(X) or predict(model, X), where:

              - model: A dictionary indicating the output of linearInterpolateFit.

              - X: A numeric vector indicating the x-coordinates of the points to be predicted.
        """
        ...


@builtin_function(_linearTimeTrend)
def linearTimeTrend(X: Constant, window: Constant) -> Constant:
    r"""Calculate the moving linear regression for X.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    window : Constant
        A positive integer indicating the size of the sliding window.

    Returns
    -------
    Constant
        A tuple with 2 elements, alpha (the Linear regression intercept LINEARREG_INTERCEPT)
        and beta (the linear regression slope LINEARREG_SLOPE).
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_linprog)
    def linprog(f: Constant, A: Constant = DFLT, b: Constant = DFLT, Aeq: Constant = DFLT, beq: Constant = DFLT, lb: Constant = DFLT, ub: Constant = DFLT, method: Constant = DFLT) -> Constant:
        r"""Solve the following optimization problem with a linear objective function and
        a set of linear constraints.

        .. math::

           \min_{x} f^T x \quad \text{such that} \quad
           \begin{cases}
           A \cdot x \le b \\
           Aeq \cdot x = beq \\
           lb \le x \le ub
           \end{cases}

        Parameters
        ----------
        A : Constant
            A matrix.
        Aeq : Constant
            A matrix. A and Aeq must be with the same number of columns.
        f : Constant
            A vector.
        b : Constant
            A vector.
        beq : Constant
            A vector.
        lb : Constant
            A  scalar or vector.
        ub : Constant
            A  scalar or vector. lb and ub are with the same length as x indicating the
            lower bounds and upper bounds of x.

            - If lb or ub is a scalar, all elements of x are subject to the same lower
              bound or upper bound constraint.

            - If lb or ub is null, there is no lower bound or upper bound constraint
              for x.

            - If lb or ub is a vector, an element of x is subject to the lower bound or
              upper bound constraint specified by the corresponding element of lb or ub.
        method : Constant
            A string indicating the optimization algorithm. It can be either 'simplex'
            (recommended) or 'interior-point'.

        Returns
        -------
        Constant
            A 2-element tuple. The first element is the minimum value of the objective
            function. The second element is the value of x where the value of the objective
            function is minimized.
        """
        ...


@builtin_function(_lj)
def lj(leftTable: Constant, rightTable: Constant, matchingCols: Constant, rightMatchingCols: Constant = DFLT, leftFilter: Constant = DFLT, rightFilter: Constant = DFLT) -> Constant:
    r"""Left join (lj) return all records from the left table and the matched records from
    the right table. The result is NULL from the right table if there is no match. If
    there are more than one matched record in the right table, all the matched records
    in the right table are returned. Left join may return more rows than the left table.

    The only difference between left semi join (lsj) and left join (lj) is that for left
    semi join, if there are more than one matched record in the right table, only the
    first record is returned. Left semi join returns the same number of rows as the left table.

    Parameters
    ----------
    leftTable : Constant
        The table to be joined.
    rightTable : Constant
        The table to be joined.
    matchingCols : Constant
        A string scalar/vector indicating the matching column(s).
    rightMatchingCols : Constant
        A string scalar/vector indicating the matching column(s) in rightTable. This optional
        argument must be specified if at least one of the matching columns has different
        names in leftTable and rightTable . The joining column names in the result will be
        the joining column names from the left table.
    leftFilter : Constant
        A condition expression used as filter condition for the columns in the left table.
        Use "and" or "or" to join multiple conditions.
    rightFilter : Constant
        A condition expression used as filter condition for the columns in the right table.
        Use "and" or "or" to join multiple conditions.
    """
    ...


@builtin_function(_loadBackup)
def loadBackup(backupDir: Constant, dbPath: Constant, partition: Constant, tableName: Constant) -> Constant:
    r"""Load the backup of a partition in a distributed table. It must be executed by a
    logged-in user.

    Parameters
    ----------
    backupDir : Constant
        A string indicating the directory where the backup is saved.
    dbPath : Constant
        A string indicating the path of a DFS database. For example: "dfs://demo".
    partition : Constant
        A string indicating the path of a partition under the database. For example: "/20190101/GOOG".
    tableName : Constant
        A string indicating a distributed table name.
    """
    ...


@builtin_function(_loadModel)
def loadModel(file: Constant) -> Constant:
    r"""Load the specifications of a trained model into memory as a dictionary.

    Parameters
    ----------
    file : Constant
        A string indicating the absolute path and name of the output file.
    """
    ...


@builtin_function(_loadNpy)
def loadNpy(fileName: Constant) -> Constant:
    r"""Load an .npy (Python Numpy) binary file and convert it into a DolphinDB vector
    or matrix. NaN in the .npy file is converted into null values in DolphinDB.

    Right now the function only works for .npy files with numerical data.

    Parameters
    ----------
    filename : Constant
        A string indicating the path and name of an .npy file.
    """
    ...


@builtin_function(_loadNpz)
def loadNpz(fileName: Constant) -> Constant:
    r"""Read an npz binary file from Python NumPy and convert it into DolphinDB objects.
    NaN in .npz file is converted into null values in DolphinDB.

    Conversion Table for Python np.array and DolphinDB Objects:

    +-------------------+---------------------------------------------------+
    | NumPy array       | DolphinDB Objects                                 |
    +===================+===================================================+
    | one-dimensional   | vector                                            |
    +-------------------+---------------------------------------------------+
    | two-dimensional   | matrix                                            |
    +-------------------+---------------------------------------------------+
    | three-dimensional | tuple (where each element represents a matrix)    |
    +-------------------+---------------------------------------------------+

    Data types supported for conversion are: BOOL, CHAR, SHORT, INT, LONG, FLOAT, DOUBLE
    and STRING (only one-dimensional array is supported).


    Parameters
    ----------
    filename : Constant
        A STRING indicating the path of .npz file.
    """
    ...


@builtin_function(_loadRecord)
def loadRecord(filename: Constant, schema: Constant, skipBytes: Constant = DFLT, count: Constant = DFLT) -> Constant:
    r"""Load a binary file with fixed length for each column into memory.

    Parameters
    ----------
    filename : Constant
        A string indicating the path of a file.
    schema : Constant
        A tuple of vectors. Each vector of the tuple represents the name and data type
        of a column. For a string column, we also need to specify the length of the string.
        If a string is shorter than the specified length, add 0s in the end to reach the
        specified length.
    skipBytes : Constant
        A nonnegative integer indicating the number of bytes to skip in the beginning of
        the file. The default value is 0.
    count : Constant
        A positive integer indicating the number of records to load. If it is not specified,
        load all records.
    """
    ...


@builtin_function(_loadTable)
def loadTable(database: Constant, tableName: Constant, partitions: Constant = DFLT, memoryMode: Constant = DFLT) -> Constant:
    r"""For a DFS table: return a table object with only the metadata.

    For a partitioned table in the local file system: if memoryMode = true, load all
    partitions (or selected partitions if parameter partitions is specified) into memory
    as a partitioned table; if memoryMode = false, only load metadata into memory.

    Parameters
    ----------
    database : Constant
        Either a database handle, or the absolute path of the folder where the database
        is stored. The database can be located in the local file system, or the distributed
        file system.
    tableName : Constant
        A string indicating the name of the table on disk.
    partitions : Constant
        A scalar or vector indicating which partitions of the table to load into memory.
    memoryMode : Constant
        A Boolean value indicating whether to load only metadata into memory (memoryMode = false).
        If memoryMode = true, load all data or selected partitions into memory. Please note
        that this parameter only takes effect for local databases on disk. For DFS databases,
        only the metadata is loaded into memory.
    """
    ...


@builtin_function(_loadText)
def loadText(filename: Constant, delimiter: Constant = DFLT, schema: Constant = DFLT, skipRows: Constant = DFLT, arrayDelimiter: Constant = DFLT, containHeader: Constant = DFLT, arrayMarker: Constant = DFLT) -> Constant:
    r"""Load a text file into memory as a table. loadText loads data in single thread.To load data in multiple threads, use ploadText.

    - How a header row is determined:

      - When containHeader is null, the first row of the file is read in string format,
        and the column names are parsed from that data. Please note that the upper limit
        for the first row is 256 KB. If none of the columns in the first row of the file
        starts with a number, the first row is treated as the header with column names of
        the text file. If at least one of the columns in the first row of the file starts
        with a number, the system uses col0, col1, … as the column names;

        - When containHeader is true, the first row is determined as the header row,
          and the column names are parsed from that data;

        - When containHeader is false, the system uses col0, col1, … as the column
          names.

    - How the column types are determined:

      - When loading a text file, the system determines the data type of each column
        based on a random sample of rows. This convenient feature may not always
        accurately determine the data type of all columns. We recommend users check
        the data type of each column with the extractTextSchema function after loading.

      - When the input file contains dates and times:

        - For data with delimiters (date delimiters "-", "/" and ".", and time delimiter
          ":"), it will be converted to the corresponding type. For example, "12:34:56"
          is converted to the SECOND type; "23.04.10" is converted to the DATE type.

        - For data without delimiters, data in the format of "yyMMdd" that meets 0<=yy<=99,
          0<=MM<=12, 1<=dd<=31, will be preferentially parsed as DATE; data in the format
          of "yyyyMMdd" that meets 1900<=yyyy<=2100, 0<=MM<=12, 1<=dd<=31 will be
          preferentially parsed as DATE.

      - If a column does not have the expected data type, then we need to enter the
        correct data type of the column in the schema table. Users can also specify
        data types for all columns. For a temporal column, if it does not have the
        expected data type, we also need to specify a format such as "MM/dd/yyyy" in
        the schema table. For details about temporal formats please refer to Parsing
        and Format of Temporal Variables.

    To load a subset of columns, specify the column index in the "col" column of schema.

    As string in DolphinDB is encoded in UTF-8, we require input text files be encoded
    in UTF-8.

    Column names in DolphinDB must only contain letters, numbers or underscores and must
    start with a letter. If a column name in the text file does not meet the requirements,
    the system automatically adjusts it:

    - If the column name contains characters other than letters, numbers or underscores,
      these characters are converted into underscores.

    - If the column name does not start with a letter, add "c" to the column name so
      that it starts with "c".

    Parameters
    ----------
    filename : Constant
        The input text file name with its absolute path. Currently only .csv files are
        supported.
    delimiter : Constant, optional
        A STRING scalar indicating the table column separator. It can consist of one
        or more characters, with the default being a comma (',').
    schema : Constant, optional
        A table. It can have the following columns, among which "name" and "type" columns
        are required.

        +--------+-------------------------+-----------------------------------+
        | Column | Data Type               | Description                       |
        +========+=========================+===================================+
        | name   | STRING scalar           | column name                       |
        +--------+-------------------------+-----------------------------------+
        | type   | STRING scalar           | data type                         |
        +--------+-------------------------+-----------------------------------+
        | format | STRING scalar           | the format of temporal columns    |
        +--------+-------------------------+-----------------------------------+
        | col    | INT scalar or vector    | the columns to be loaded          |
        +--------+-------------------------+-----------------------------------+

        .. note::

            If "type" specifies a temporal data type, the format of the source data must
            match a DolphinDB temporal data type. If the format of the source data and
            the DolphinDB temporal data types are incompatible, you can specify the column
            type as STRING when loading the data and convert it to a DolphinDB temporal
            data type using the temporalParse function afterwards.

    skipRows : Constant, optional
        An integer between 0 and 1024 indicating the rows in the beginning of the text
        file to be ignored. The default value is 0.
    arrayDelimiter : Constant, optional
        A single character indicating the delimiter for columns holding the array vectors
        in the file. You must use the schema parameter to update the data type of the
        type column with the corresponding array vector data type before import.
    containHeader : Constant, optional
        A Boolean value indicating whether the file contains a header row. The default
        value is null.
    arrayMarker : Constant, optional
        A string containing 2 characters or a CHAR pair. These two characters represent
        the identifiers for the left and right boundaries of an array vector. The default
        identifiers are double quotes (").

        - It cannot contain spaces, tabs (``\t``), or newline characters (``\t`` or ``\n``).

        - It cannot contain digits or letters.

        - If one is a double quote (``"``), the other must also be a double quote.

        - If the identifier is ``'``, ``"``, or ``\``, a backslash ( ``\`` ) escape character should
          be used as appropriate. For example, ``arrayMarker="\"\""``.

        - If delimiter specifies a single character, arrayMarker cannot contain the
          same character.

        - If delimiter specifies multiple characters, the left boundary of arrayMarker
          cannot be the same as the first character of delimiter.
    """
    ...


@builtin_function(_loadTextEx)
def loadTextEx(dbHandle: Constant, tableName: Constant, partitionColumns: Constant, filename: Constant, delimiter: Constant = DFLT, schema: Constant = DFLT, skipRows: Constant = DFLT, transform: Constant = DFLT, sortColumns: Constant = DFLT, atomic: Constant = DFLT, arrayDelimiter: Constant = DFLT, containHeader: Constant = DFLT, arrayMarker: Constant = DFLT, chunkSize: Constant = DFLT) -> Constant:
    r"""Load a text file into DolphinDB database.

    If dbHandle is specified and is not empty string "": load a text file to a distributed
    database. The result is a table object with metadata of the table.

    If dbHandle is empty string "" or unspecified: load a text file as a partitioned in-memory
    table. For this usage, when we define dbHandle with function database, the parameter
    directory must also be the empty string "" or unspecified.

    If parameter transform is specified, we need to first execute createPartitionedTable
    and then load the data. The system will apply the function specified in parameter transform
    and then save the results into the database.

    Function loadTextEx and function loadText share many common features, such as whether
    the first row is treated as the header, how the data types of columns are determined,
    how the system adjusts illegal column names, etc. For more details, please refer to
    function loadText.

    Parameters
    ----------
    dbHandle : Constant
        The distributed database where the imported data will be saved. The database
        can be either in the distributed file system or an in-memory database.
    tableName : Constant
        A string indicating the name of the table with the imported data.
    partitionColumns : Constant
        A string scalar/vector indicating partitioning column(s). For sequential partition,
        partitionColumns is "" as it doesn't need a partitioning column. For composite
        partition, partitionColumns is a string vector.
    filename : Constant
        The input text file name with its absolute path. Currently only .csv files are
        supported.
    delimiter : Constant, optional
        A STRING scalar indicating the table column separator. It can consist of one
        or more characters, with the default being a comma (',').
    schema : Constant, optional
        A table. It can have the following columns, among which "name" and "type" columns
        are required.

        +--------+----------------------+-----------------------------------+
        | Column | Data Type            | Description                       |
        +========+======================+===================================+
        | name   | STRING scalar        | column name                       |
        +--------+----------------------+-----------------------------------+
        | type   | STRING scalar        | data type                         |
        +--------+----------------------+-----------------------------------+
        | format | STRING scalar        | the format of temporal columns    |
        +--------+----------------------+-----------------------------------+
        | col    | INT scalar or vector | the columns to be loaded          |
        +--------+----------------------+-----------------------------------+

        .. note::

            If "type" specifies a temporal data type, the format of the source data must
            match a DolphinDB temporal data type. If the format of the source data and the
            DolphinDB temporal data types are incompatible, you can specify the column type
            as STRING when loading the data and convert it to a DolphinDB temporal data type
            using the temporalParse function afterwards.

    skipRows : Constant, optional
        An integer between 0 and 1024 indicating the rows in the beginning of the text
        file to be ignored. The default value is 0.
    transform : Constant, optional
        A unary function. The parameter of the function must be a table.
    sortColumns : Constant, optional
        A string scalar/vector indicating the columns based on which the table is sorted.
    atomic : Constant, optional
        A Boolean value indicating whether to guarantee atomicity when loading a file
        with the cache engine enabled. If it is set to true, the entire loading process
        of a file is a transaction; set to false to split the loading process into multiple
        transactions.

        .. note::

            It is required to set atomic = false if the file to be loaded exceeds the
            cache engine capacity. Otherwise, a transaction may get stuck: it can neither
            be committed nor rolled back.

    arrayDelimiter : Constant, optional
        A single character indicating the delimiter for columns holding the array vectors
        in the file. Since the array vectors cannot be recognized automatically, you must
        use the schema parameter to update the data type of the type column with the
        corresponding array vector data type before import.
    containHeader : Constant, optional
        A Boolean value indicating whether the file contains a header row. The default
        value is null. See loadText for the detailed determining rules.
    arrayMarker : Constant
        A string containing 2 characters or a CHAR pair. These two characters represent
        the identifiers for the left and right boundaries of an array vector. The default
        identifiers are double quotes (").

        - It cannot contain spaces, tabs (``\t``), or newline characters (``\t`` or ``\n``).

        - It cannot contain digits or letters.

        - If one is a double quote (``"``), the other must also be a double quote.

        - If the identifier is ``'``, ``"``, or ``\``, a backslash ( ``\`` ) escape character should
          be used as appropriate. For example, ``arrayMarker="\"\""``.

        - If delimiter specifies a single character, arrayMarker cannot contain the
          same character.

        - If delimiter specifies multiple characters, the left boundary of arrayMarker
          cannot be the same as the first character of delimiter.
    chunkSize : Constant
        A positive integer with a default value of 128 (in MB). It specifies the maximum
        size of each chunk during parallel import. The upper limit is max(maxMemSize /
        workerNum, 128MB), representing the greater of the maximum available memory per
        worker and 128MB.
    """
    ...


@builtin_function(_loc)
def loc(obj: Constant, rowFilter: Constant, colFilter: Constant = DFLT, view: Constant = DFLT) -> Constant:
    r"""Access a group of rows and columns of a matrix by label(s) or a boolean vector.

    Parameters
    ----------
    obj : Constant
        A matrix object. It can be a standard matrix, an indexed series or an indexed
        matrix.
    rowFilter : Constant
        Can be:

        - a Boolean vector - the rows/columns marked as true will be returned. The
          length of the vector must match the number of rows/columns of obj.

        - a scalar, a vector or a pair whose data type is compatible with the row/
          column labels of obj. A pair indicates the selection range (both upper
          bound and lower bound are inclusive).
    colFilter : Constant
        Can be:

        - a Boolean vector - the rows/columns marked as true will be returned. The
          length of the vector must match the number of rows/columns of obj.

        - a scalar, a vector or a pair whose data type is compatible with the row/
          column labels of obj. A pair indicates the selection range (both upper
          bound and lower bound are inclusive).

        .. note::

            If rowFilter/colFilter is a pair, then obj must be an indexed series or an indexed matrix.

            Data type compatibility rules:

            - INT, SHORT, LONG and CHAR are compatible

            - FLOAT and DOUBLE are compatible

            - STRING and SYMBOL are compatible

    view : Constant
        A Boolean value. The default value is false indicating the result will be a
        copy of the original matrix (deep copy). If set to true, the result will be
        a view on the original matrix (shallow copy) and changes made to the original
        matrix will be reflected in the view.

    Returns
    -------
    Constant
        A copy or a view of the original matrix.
    """
    ...


@builtin_function(_localtime)
def localtime(X: Constant) -> Constant:
    r"""Convert X in GMT (Greenwich Mean Time) to local time zone.

    Parameters
    ----------
    X : Constant
        A variable/vector. The data type of X can be datetime, timestamp, or nanotimestamp.
    """
    ...


@builtin_function(_loess)
def loess(X: Constant, Y: Constant, resampleRule: Constant, closed: Constant = DFLT, origin: Constant = DFLT, outputX: Constant = DFLT, bandwidth: Constant = DFLT, robustnessIter: Constant = DFLT, accuracy: Constant = DFLT) -> Constant:
    r"""Resample X based on the specified resampleRule, closed and origin. Implement
    Local Regression Algorithm (Loess) for interpolation on Y based on the resampled X.

    If outputX is unspecified, return a vector of Y after the interpolation.

    If outputX=true, return a tuple where the first element is the vector of resampled
    X and the second element is a vector of Y after the interpolation.

    Parameters
    ----------
    X : Constant
        A strictly increasing vector of temporal type.
    Y : Constant
        A numeric vector of the same length as X.
    resampleRule : Constant
        A string. See the parameter rule of function resample for the optional values.
    closed : Constant, optional
        A string indicating which boundary of the interval is closed.
        The default value is 'left' for all values of rule except for 'M', 'A',
        'Q', 'BM', 'BA', 'BQ', and 'W' which all have a default of 'right'.

        The default is 'right' if origin is 'end' or 'end_day'.
    origin : Constant, optional
        A string or a scalar of the same data type as X, indicating the timestamp where
        the intervals start. It can be 'epoch', start', 'start_day', 'end', 'end_day'
        or a user-defined time object. The default value is 'start_day'.

        - 'epoch': origin is 1970-01-01

        - 'start': origin is the first value of the timeseries

        - 'start_day': origin is 00:00 of the first day of the timeseries

        - 'end': origin is the last value of the timeseries

        - 'end_day': origin is 24:00 of the last day of the timeseries
    outputX : Constant
        A Boolean value indicating whether to output the resampled X. The default value
        is false.
    bandwidth : Constant
        A numeric scalar in (0,1]. when computing the loess fit at a particular point,
        this fraction of source points closest to the current point is taken into
        account for computing a least-squares regression.
    robustnessIter : Constant
        A postive interger indicating how many robustness iterations are done.
    accuracy : Constant
        A number greater than 1. If the median residual at a certain robustness iteration
        is less than this amount, no more iterations are done.
    """
    ...


@builtin_function(_log)
def log(X: Constant, Y: Constant = DFLT) -> Constant:
    r"""If Y is not specified: return the natural logarithm of X.

    If Y is specified: return the logarithm of X to base Y.

    Parameters
    ----------
    X : Constant
        A scalar/vector/pair/matrix/table.
    Y : Constant, optional
        A positive number indicating the base.
    """
    ...


@builtin_function(_log10)
def log10(X: Constant) -> Constant:
    r"""Return the logarithm of X to the base 10.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_log1p)
def log1p(X: Constant) -> Constant:
    r"""Return log(1+X).

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_log2)
def log2(X: Constant) -> Constant:
    r"""Return the logarithm of X to the base 2.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_logisticRegression)
def logisticRegression(ds: Constant, yColName: Constant, xColNames: Constant, intercept: Constant = DFLT, initTheta: Constant = DFLT, tolerance: Constant = DFLT, maxIter: Constant = DFLT, regularizationCoeff: Constant = DFLT, numClasses: Constant = DFLT) -> Constant:
    r"""Fit a logistic regression model. The result is a dictionary with the following
    keys: iterations, modelName, coefficients, tolerance, logLikelihood, xColNames and
    intercept. iterations is the number of iterations, modelName is "Logistic Regression",
    coefficients is a vector of the parameter estimates, logLikelihood is the final
    value of the log likelihood function.

    The fitted model can be used as an input for function predict.

    Parameters
    ----------
    ds : Constant
        The data source to be trained. It can be generated with function sqlDS.
    yColName : Constant
        A string indicating the category column name.
    xColNames : Constant
        A string scalar/vector indicating the names of independent variables.
    intercept : Constant, optional
        A Boolean scalar indicating whether the regression uses an intercept. The
        default value is true, which means that a column of 1s is added to the independent
        variables.
    initTheta : Constant, optional
        A vector indicating the initial values of the parameters when the iterations
        begin. The default value is a vector of zeroes with the length of xColNames.size()+intercept.
    tolerance : Constant, optional
        A numeric scalar. If the difference in the value of the log likelihood functions
        of 2 adjacent iterations is smaller than tolerance, the iterations would stop.
        The default value is 0.001.
    maxIter : Constant, optional
        A positive integer indicating the maximum number of iterations. The iterations
        will stop if the number of iterations reaches maxIter. The default value is 500.
    regularizationCoeff : Constant, optional
        A positive number indicating the coefficient of the regularization term. The
        default value is 1.0.
    """
    ...


@builtin_function(_long)
def long(X: Constant) -> Constant:
    r"""Convert the data type of X to LONG.

    Parameters
    ----------
    X : Constant
        Can be of any data type.
    """
    ...


@builtin_function(_loop)
def loop(func: Constant, *args) -> Constant:
    r"""The loop template is very similar to the each template. Their difference is
    about the data form and data type of the function call results.

        For the each template, the data types and forms of the return value are determined
        by each calculation result. It returns a vector or matrix if all calculation
        results have the same data type and form, otherwise it returns a tuple.

        The loop template always returns a tuple.

    Parameters
    ----------
    func : Constant
        A function.
    args : Constant
        The required parameter of func.
    X : Constant
        The required parameter of func.
    Y : Constant
        The required parameter of func.
    """
    ...


@builtin_function(_lowDouble)
def lowDouble(X: Constant) -> Constant:
    r"""It returns the low-order 8-byte double data of X.

    Parameters
    ----------
    X : Constant
        A vector/scalar which must be 16-byte data type.
    """
    ...


@builtin_function(_lowLong)
def lowLong(X: Constant) -> Constant:
    r"""It returns the low-order 8-byte long integer data of X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/table/data pair/dictionary which must be 16-byte data type
        (UUID, IPADDR, INT128, COMPLEX, and POINT are supported).
    """
    ...


@builtin_function(_lowRange)
def lowRange(X: Constant) -> Constant:
    r"""For each element Xi in X, count the continuous nearest neighbors to its left
    that are larger than Xi.

    For each element in X, the function return the maximum length of a window to the
    left of X where it is the max/min. For example, after how many days a stock hits
    a new high.

    Parameters
    ----------
    X : Constant
        A vector/tuple/matrix/table.
    """
    ...


@builtin_function(_lower)
def lower(X: Constant) -> Constant:
    r"""Convert all characters in a string or a list of strings into lower cases.

    If X is a table, the function is applied only to columns of character types (CHAR,
    STRING, or SYMBOL). Other column types are ignored.

    Parameters
    ----------
    X : Constant
        A CHAR/STRING/SYMBOL scalar, vector, or table.
    """
    ...


@builtin_function(_lowerBound)
def lowerBound(X: Constant, Y: Constant) -> Constant:
    r"""For each element y in Y, get the first element that is greater than or equal
    to y and return its index in X. If no element is found, return the length of X.

    Parameters
    ----------
    X : Constant
        An increasing vector, or an indexed series/matrix.
    Y : Constant
        A scalar, vector, array vector, tuple, matrix, dictionary or table.
    """
    ...


@builtin_function(_lpad)
def lpad(str: Constant, length: Constant, pattern: Constant = DFLT) -> Constant:
    r"""Pad the left-side of a string with a specific set of characters.

    If str is a table, the function is applied only to columns of STRING type. Other
    column types are ignored.

    Parameters
    ----------
    str : Constant
        A STRING scalar/vector, or table. It is the string to pad characters to (the
        left-hand side).
    length : Constant
        A positive integer indicating the number of characters to return. If length
        is smaller than the length of str, the lpad function is equivalent to left(str,
        length).
    pattern : Constant
        A string scalar. It is the string that will be padded to the left-hand side
        of str. If it is unspecified, the lpad function will pad spaces to the left-side
        of str.
    """
    ...


@builtin_function(_lshift)
def lshift(X: Constant, bits: Constant) -> Constant:
    r"""Shift the binary representation of X to the left by bits. The bits on the right
    are filled with zeros.

    Parameters
    ----------
    X : Constant
        An integral scalar/pair/vector/matrix/table.
    bits : Constant
        The number of bits to shift.
    """
    ...


@builtin_function(_lsj)
def lsj(leftTable: Constant, rightTable: Constant, matchingCols: Constant, rightMatchingCols: Constant = DFLT, leftFilter: Constant = DFLT, rightFilter: Constant = DFLT) -> Constant:
    r"""Left join (lj) return all records from the left table and the matched records
    from the right table. The result is NULL from the right table if there is no match.
    If there are more than one matched record in the right table, all the matched records
    in the right table are returned. Left join may return more rows than the left table.

    The only difference between left semi join (lsj) and left join (lj) is that for left
    semi join, if there are more than one matched record in the right table, only the
    first record is returned. Left semi join returns the same number of rows as the left
    table.

    Parameters
    ----------
    leftTable : Constant
        The table to be joined.
    rightTable : Constant
        The table to be joined.
    matchingCols : Constant
        A string scalar/vector indicating the matching column(s).
    rightMatchingCols : Constant
        A string scalar/vector indicating the matching column(s) in rightTable. This optional
        argument must be specified if at least one of the matching columns has different
        names in leftTable and rightTable . The joining column names in the result will be
        the joining column names from the left table.
    leftFilter : Constant
        A condition expression used as filter condition for the columns in the left table.
        Use "and" or "or" to join multiple conditions.
    rightFilter : Constant
        A condition expression used as filter condition for the columns in the right table.
        Use "and" or "or" to join multiple conditions.
    """
    ...


@builtin_function(_lt)
def lt(X: Constant, Y: Constant) -> Constant:
    r"""If neither X nor Y is a set, return the element-by-element comparison of X<Y.

    If both X and Y are sets, check if X is a proper subset of Y.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix/set.
    Y : Constant
        A scalar/pair/vector/matrix/set. If X or Y is a pair/vector/matrix, the other
        is a scalar or a pair/vector/matrix of the same size.
    """
    ...


@builtin_function(_ltrim)
def ltrim(X: Constant) -> Constant:
    r"""Remove leading spaces from a character expression.

    If X is a table, the function is applied only to columns of STRING type. Other
    column types are ignored.

    Parameters
    ----------
    X : Constant
        A STRING scalar/vector, or table.
    """
    ...


@builtin_function(_lu)
def lu(obj: Constant, permute: Constant = DFLT) -> Constant:
    r"""Compute pivoted LU decomposition of a matrix.

    If permute is false, return 3 matrices (L, U and P) with obj = P'LU. P is a permutation
    matrix, L is a lower triangular matrix with unit diagonal elements, and U is an upper
    triangular matrix.

    If permute is true, return 2 matrices (L and U) with obj = L*U.

    Parameters
    ----------
    obj : Constant
        A matrix with no null values.
    permute : Constant
        A Boolean value. The default value is false.
    """
    ...


@builtin_function(_mLowRange)
def mLowRange(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""For each element Xi in a sliding window of X, count the continuous nearest neighbors
    to its left that are larger than Xi. Null values are treated as the minimum values.

    If X is a matrix, conduct the aforementioned calculation within each column of X.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.

    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mTopRange)
def mTopRange(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""For each element Xi in a sliding window of X, count the continuous nearest neighbors
    to its left that are smaller than Xi. Null values are treated as the minimum values.

    If X is a matrix, conduct the aforementioned calculation within each column of X.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.

    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_ma)
def ma(X: Constant, window: Constant, maType: Constant) -> Constant:
    r"""Calculate the moving average (whose type is determined by maType) in a sliding
    window of the given length.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    window : Constant
        A positive integer indicating the size of the sliding window.
    maType : Constant
        The type of moving averages. It is an integer in [0,8].0= sma , 1= ema , 2= wma ,
        3= dema , 4= tema , 5= trima , 6= kama , 8= t3 . Note that value 7 (mama) is not supported.
    """
    ...


@builtin_function(_mad)
def mad(X: Constant, useMedian: Constant = DFLT) -> Constant:
    r"""If X is a vector, return the average absolute deviation of X.

    If X is a matrix, the calculation is based on each column and returns a matrix.

    If X is a table, the calculation is based on each column and returns a table.

    As with all aggregate functions, null values are not included in the calculation.

    Parameters
    ----------
    X : Constant
        A vector, matrix or table.
    useMedian : Constant
        A Boolean value indicating whether the result is generated with the median
        absolute deviation or the mean absolute deviation. The default value is false
        and it returns the mean absolute deviation.

        - Mean Absolute Deviation: mean(abs(X - mean(X)))

        - Median Absolute Deviation: med(abs(X - med(X)))
    """
    ...


@builtin_function(_makeCall)
def makeCall(func: Constant, *args) -> Constant:
    r"""Call a function with the specified parameters to generate a piece of script.
    The difference between call and makeCall is that makeCall doesn't execute the script.

    Parameters
    ----------
    F : Constant
        A function.
    args : Constant
        The required parameters of F.
    """
    ...


@builtin_function(_makeKey)
def makeKey(*args) -> Constant:
    r"""Combine the specified args as a BLOB scalar or vector, so it can used as the
    key(s) of a dictionary or a set. Compared with makeSortedKey, makeKey keeps the
    order of the inputs in the result.

    Parameters
    ----------
    args : Constant
        Multiple scalars or vectors of the same length.
    """
    ...


@builtin_function(_makeSortedKey)
def makeSortedKey(*args) -> Constant:
    r"""Combine the specified args as a BLOB scalar or vector. makeSortedKey stores the
    keys in sorted order internally, while returns the same result as makeKey.

    Parameters
    ----------
    args : Constant
        Multiple scalars or vectors of the same length.
    """
    ...


@builtin_function(_makeUnifiedCall)
def makeUnifiedCall(func: Constant, args: Constant) -> Constant:
    r"""Generate metacode for function call. Use function eval to execute the metacode.
    The difference between makeUnifiedCall and the template function unifiedCall is
    that makeUnifiedCall doesn't execute the metacode.

    Parameters
    ----------
    func : Constant
        A function.
    args : Constant
        A tuple. Each element is a parameter of func.
    """
    ...


@builtin_function(_mannWhitneyUTest)
def mannWhitneyUTest(X: Constant, Y: Constant, correct: Constant = DFLT) -> Constant:
    r"""Perform the Mann-Whitney U test on X and Y.

    Parameters
    ----------
    X : Constant
        A numeric vector.
    Y : Constant
        A numeric vector.
    correct : Constant
        A Boolean value indicating whether to consider continuity correction when
        calculating the p-value. The default value is true.

    Returns
    -------
    Constant
        A dictionary object with the following keys:

        - stat: A table containing p-values under three different alternative hypotheses

        - correct: Whether to consider continuity correction when calculating p-value

        - method: The string "Mann-Whitney U test"

        - U: U statistic
    """
    ...


@builtin_function(_manova)
def manova(X: Constant, group: Constant) -> Constant:
    r"""Conduct multivariate analysis of variance (MANOVA).

    Parameters
    ----------
    X : Constant
        A matrix or a table whose columns are all of numeric types.
    group : Constant
        A vector with the same length as each of the columns of X indicating groups.
    """
    ...


@builtin_function(_mask)
def mask(X: Constant, Y: Constant) -> Constant:
    r"""Apply Y on each element of X. If the result is false, keep the element; if the
    result is true, change it to null. The result is of the same length as X.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix.
    Y : Constant
        A conditional expression that generates true or false.
    """
    ...


@builtin_function(_matrix)
def matrix(dataType: Constant, rows: Constant, cols: Constant, columnsCapacity: Constant = DFLT, defaultValue: Constant = DFLT) -> Constant:
    r"""Generate a matrix.

    Parameters
    ----------
    dataType : Constant
        The data type of the matrix. Data types other than INT128, UUID, IPADDR, POINT
        and DURATION are supported.
    rows : Constant
        The number of rows.
    cols : Constant
        The number of cols.
    columnsCapacity : Constant
        The amount of memory (in terms of the number of columns) allocated to the matrix.
        When the number of columns exceeds columnsCapacity, the system will first allocate
        memory of 1.2~2 times of capacity, copy the data to the new memory space, and
        release the original memory.
    defaultValue : Constant
        The default value for the elements of the matrix. Without specifying defaultValue,
        all elements in the matrix are 0s for integers/doubles and null values for symbols.
    """
    ...


@builtin_function(_mavg)
def mavg(X: Constant, window: Union[Alias[Literal["weights"]], Constant], minPeriods: Constant = DFLT) -> Constant:
    r"""If X is a vector, return a vector of the same length as X. If the second parameter is:

    - window: Calculate the moving averages of X in a sliding window of length window.

    - weights: A weight vector used to alculate the moving weighted averages of X in a
      sliding window of length weights. The order of weights corresponds one-to-one with
      the data in the window. The length of weights (the weight vector) must be in [0,1024].
      Return NULL for the first (size(weights) - 1) elements. If weights is specified, the
      parameter minPeriods doesn't take effect.

    If X is a matrix/table, conduct the aforementioned calculation within each column of X.
    The result is a matrix with the same shape as X.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size of
        the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.

    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window required
        to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mavgTopN)
def mavgTopN(X: Constant, S: Constant, window: Constant, top: Constant, ascending: Constant = DFLT, tiesMethod: Constant = DFLT) -> Constant:
    r"""Within a sliding window of given length (measured by the number of elements), the
    function stably sorts X by S in the order specified by ascending, then calculates
    the average of the first top elements.

    Parameters
    ----------
    X : Constant
        A numeric vector or matrix.
    S : Constant
        A numeric/temporal vector or matrix, based on which X are sorted.
    window : Constant
        An integer greater than 1, indicating the sliding window size.
    top : Constant
        An integer in (1, window], indicating the first top elements of X after sorted
        based on S.
    ascending : Constant, optional
        A Boolean value indicating whether to sort S in ascending order. The default value
        is true.
    tiesMethod : Constant, optional
        A string that specifies how to select elements if there are more elements with
        the same value than spots available in the top N after sorting X within a sliding
        window. It can be:

        - 'oldest': select elements starting from the earliest entry into the window;

        - 'latest': select elements starting from the latest entry into the window;

        - 'all': select all elements.

        .. note::

            For backward compatibility, the default value of tiesMethod is 'oldest' for
            the following functions: mstdTopN, mstdpTopN, mvarTopN, mvarpTopN, msumTopN,
            mavgTopN, mwsumTopN, mbetaTopN, mcorrTopN, mcovarTopN; For the remaining mTopN
            functions, the default value of tiesMethod is 'latest'.
    """
    ...


@builtin_function(_max)
def max(X: Constant, Y: Constant = DFLT) -> Constant:
    r"""For one input:

    - If X is a vector, return the maximum in X.

    - If X is a matrix, return a vector composed of the maximum in each column of X.

    - If X is a table, return a table composed of the maximum in each column of X.

    For two inputs:

    - If Y is a scalar, compare it with each element in X, replace the element in X
      with the larger value.

    - If Y and X are of the same type and length, compare the corresponding elements
      of them and return a result containing each larger value.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    Y : Constant, optional
        A scalar, a vector of the same length as X or a matrix.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_maxDrawdown)
    def maxDrawdown(X: Constant, ratio: Constant = DFLT) -> Constant:
        r"""Calculate the maximum drawdown for the input X. Null values are ignored in calculation.

        Parameters
        ----------
        X : Constant
            A numeric vector, indicating the input data for calculating maximum drawdown
            (MDD), commonly cumulative return (or rate).
        ratio : Constant, optional
            A Boolean scalar indicating whether to express the MDD in ratio or absolute value.

            - true (default): Return the ratio of MDD over the peak.

            - false: Return the absolute value of MDD.

        Returns
        -------
        Constant
            A scalar of the same type as X.
        """
        ...


@builtin_function(_maxIgnoreNull)
def maxIgnoreNull(X: Constant, Y: Constant) -> Constant:
    r"""A binary scalar function that returns the maximum by comparing X with Y.

    Difference between max and maxIgnoreNull:

    - max: Null values are treated as the minimum value if nullAsMinValueForComparison=true,
      otherwise comparison involving null values returns NULL.

    - maxIgnoreNull: Null values are ignored in comparison and non-null maximum is returned.
      If both elements in X and Y are null, NULL is returned. This function is not affected
      by configuration parameter nullAsMinValueForComparison.

    Parameters
    ----------
    X : Constant
        A numeric, LITERAL or TEMPORAL scalar, pair, vector or matrix.
    Y : Constant
        A numeric, LITERAL or TEMPORAL scalar, pair, vector or matrix.
    """
    ...


@builtin_function(_maxPositiveStreak)
def maxPositiveStreak(X: Constant) -> Constant:
    r"""If X is a vector: return the maximum value of of the sum of consecutive positive
    elements of X.

    If X is a matrix, return the maximum value of of the sum of consecutive positive
    elements in each column of X.

    maxPositiveStreak(X) = max(cumPositiveStreak(X))

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix. The elements of X must be logic or integer values.
    """
    ...


@builtin_function(_mbeta)
def mbeta(Y: Constant, X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Calculate the coefficient estimate of an ordinary-least-squares regression of
    Y on X in a sliding window.

    Parameters
    ----------
    Y : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mbetaTopN)
def mbetaTopN(X: Constant, Y: Constant, S: Constant, window: Constant, top: Constant, ascending: Constant = DFLT, tiesMethod: Constant = DFLT) -> Constant:
    r"""Within a sliding window of given length (measured by the number of elements),
    the function stably sorts X and Y by S in the order specified by ascending, then
    calculates the coefficient estimate ordinary-least-squares regressions of Y on X.

    Parameters
    ----------
    X : Constant
        A numeric vector or matrix.
    Y : Constant
        A numeric vector or matrix.
    S : Constant
        A numeric/temporal vector or matrix, based on which X are sorted.
    window : Constant
        An integer greater than 1, indicating the sliding window size.
    top : Constant
        An integer in (1, window], indicating the first top elements of X after sorted
        based on S.
    ascending : Constant, optional
        A Boolean value indicating whether to sort S in ascending order. The default
        value is true.
    tiesMethod : Constant, optional
        A string that specifies how to select elements if there are more elements with
        the same value than spots available in the top N after sorting X within a sliding
        window. It can be:

        - 'oldest': select elements starting from the earliest entry into the window;

        - 'latest': select elements starting from the latest entry into the window;

        - 'all': select all elements.

        .. note::

            For backward compatibility, the default value of tiesMethod is 'oldest' for
            the following functions: mstdTopN, mstdpTopN, mvarTopN, mvarpTopN, msumTopN,
            mavgTopN, mwsumTopN, mbetaTopN, mcorrTopN, mcovarTopN; For the remaining mTopN
            functions, the default value of tiesMethod is 'latest'.
    """
    ...


@builtin_function(_mcorr)
def mcorr(X: Constant, Y: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Calculate the correlation of X and Y in a sliding window.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    Y : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mcorrTopN)
def mcorrTopN(X: Constant, Y: Constant, S: Constant, window: Constant, top: Constant, ascending: Constant = DFLT, tiesMethod: Constant = DFLT) -> Constant:
    r"""Within a sliding window of given length (measured by the number of elements), the
    function stably sorts X and Y by S in the order specified by ascending, then calculates
    the moving correlation of the first top pairs of elements in X and Y.

    Parameters
    ----------
    X : Constant
        A numeric vector or matrix.
    Y : Constant
        A numeric vector or matrix.
    S : Constant
        A numeric/temporal vector or matrix, based on which X are sorted.
    window : Constant
        An integer greater than 1, indicating the sliding window size.
    top : Constant
        An integer in (1, window], indicating the first top elements of X after sorted
        based on S.
    ascending : Constant, optional
        A Boolean value indicating whether to sort S in ascending order. The default
        value is true.
    tiesMethod : Constant, optional
        A string that specifies how to select elements if there are more elements with
        the same value than spots available in the top N after sorting X within a sliding
        window. It can be:

        - 'oldest': select elements starting from the earliest entry into the window;

        - 'latest': select elements starting from the latest entry into the window;

        - 'all': select all elements.

        .. note::

            For backward compatibility, the default value of tiesMethod is 'oldest' for
            the following functions: mstdTopN, mstdpTopN, mvarTopN, mvarpTopN, msumTopN,
            mavgTopN, mwsumTopN, mbetaTopN, mcorrTopN, mcovarTopN; For the remaining mTopN
            functions, the default value of tiesMethod is 'latest'.
    """
    ...


@builtin_function(_mcount)
def mcount(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Return the number of non-null values of X in a sliding window.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mcovar)
def mcovar(X: Constant, Y: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Calculate the moving covariance of X and Y in a sliding window.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    Y : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mcovarTopN)
def mcovarTopN(X: Constant, Y: Constant, S: Constant, window: Constant, top: Constant, ascending: Constant = DFLT, tiesMethod: Constant = DFLT) -> Constant:
    r"""Within a sliding window of given length (measured by the number of elements), the
    function stably sorts X and Y by S in the order specified by ascending, then calculates
    the moving covariance of the first top pairs of elements in X and Y.

    Parameters
    ----------
    X : Constant
        A numeric vector or matrix.
    Y : Constant
        A numeric vector or matrix.
    S : Constant
        A numeric/temporal vector or matrix, based on which X are sorted.
    window : Constant
        An integer greater than 1, indicating the sliding window size.
    top : Constant
        An integer in (1, window], indicating the first top elements of X after sorted
        based on S.
    ascending : Constant, optional
        A Boolean value indicating whether to sort S in ascending order. The default
        value is true.
    tiesMethod : Constant, optional
        A string that specifies how to select elements if there are more elements with
        the same value than spots available in the top N after sorting X within a sliding
        window. It can be:

        - 'oldest': select elements starting from the earliest entry into the window;

        - 'latest': select elements starting from the latest entry into the window;

        - 'all': select all elements.

        .. note::

            For backward compatibility, the default value of tiesMethod is 'oldest' for
            the following functions: mstdTopN, mstdpTopN, mvarTopN, mvarpTopN, msumTopN,
            mavgTopN, mwsumTopN, mbetaTopN, mcorrTopN, mcovarTopN; For the remaining mTopN
            functions, the default value of tiesMethod is 'latest'.
    """
    ...


@builtin_function(_md5)
def md5(X: Constant) -> Constant:
    r"""Create an MD5 hash from STRING. The result is of data type INT128.

    Parameters
    ----------
    X : Constant
        A string scalar/vector.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_mdd)
    def mdd(X: Constant, ratio: Constant = DFLT) -> Constant:
        r"""Alias for maxDrawdown. Calculate the maximum drawdown for the input X.
        Null values are ignored in calculation.

        Parameters
        ----------
        X : Constant
            A numeric vector, indicating the input data for calculating maximum drawdown
            (MDD), commonly cumulative return (or rate).
        ratio : Constant, optional
            A Boolean scalar indicating whether to express the MDD in ratio or absolute value.

            - true (default): Return the ratio of MDD over the peak.

            - false: Return the absolute value of MDD.

        Returns
        -------
        Constant
            A scalar of the same type as X.
        """
        ...


@builtin_function(_mean)
def mean(X: Constant) -> Constant:
    r"""Calculate the average of X.

    - If X is a matrix, calculate the average of each column and return a vector.

    - If X is a table, calculate the average of each column and return a table.

    This function is equivalent to avg.

    The calculation skips null values.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_med)
def med(X: Constant) -> Constant:
    r"""If X is a vector, return the median of all the elements in X.

    If X is a matrix, calculate the median of each column of X and return a vector.

    As with all aggregate functions, null values are not included in the calculation.

    Please note that the data type of the result is always DOUBLE.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix.
    """
    ...


@builtin_function(_mem)
def mem(freeUnusedBlocks: Constant = DFLT) -> Constant:
    r"""Display the memory usage of the current node. If freeUnusedBlocks=true, free
    unused memory blocks.

    Parameters
    ----------
    freeUnusedBlocks : Constant
        A Boolean value indicating whether to free unused memory blocks. The default
        value is false.
    """
    ...


@builtin_function(_member)
def member(obj: Constant, keys: Constant) -> Constant:
    r"""Return the specified member/attribute of an object.

    Parameters
    ----------
    X : Constant
        A table/dictionary.
    Y : Constant
        A member/attribute of X.
    """
    ...


@builtin_function(_memberModify_)
def memberModify_(obj: Constant, function: Constant, indices: Constant, parameters: Constant = DFLT) -> Constant:
    r"""Modifies one or more member objects of obj by applying a specified function with
    given parameters.

    Parameters
    ----------
    obj : Constant
        A tuple, a dictionary with values of ANY type, or a class instance.
    function : Constant
        A built-in function that accepts a mutable first parameter (e.g., append_).
    indices : Constant
        Specifies which members to modify. It can be:

        - A scalar: Modifies a single member

        - A vector: Modifies multiple members, with each element identifying a member

        - A tuple: Modifies one or multiple members through multi-dimensional indexing,
          where tuple length represents indexing depth
    parameters : Constant, optional
        Indicates additional parameters passed to function after its first parameter.
        If function only takes a single parameter (obj), leave parameters unspecified
        or pass an empty tuple.
    """
    ...


@builtin_function(_merge)
def merge(left: Constant, right: Constant, how: Constant = DFLT) -> Constant:
    r"""Merge 2 indexed series or 2 indexed matrices.

    Parameters
    ----------
    left : Constant
        An indexed series, or an indexed matrix.
    right : Constant
        An indexed series, or an indexed matrix.
    how : Constant
        A string indicating how to merge left and right. It can take the value of
        'inner', 'outer', 'left', 'right', or 'asof'. The default value is 'inner'.
    """
    ...


@builtin_function(_mfirst)
def mfirst(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Return the first element of X in a sliding window.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mfirstNot)
def mfirstNot(X: Constant, window: Constant, k: Constant = DFLT, minPeriods: Constant = DFLT) -> Constant:
    r"""If X is a vector:

    - If k is not specified, return the first element of X that is not null in a
      sliding window.

    - If k is specified, return the first element of X that is neither k nor null
      in the window.

    If X is a matrix or table, conduct the aforementioned calculation within each
    column of X. The result is a vector.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    k : Constant, optional
        A numeric or string scalar indicating the value to be matched.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_microsecond)
def microsecond(X: Constant) -> Constant:
    r"""For each element in X, return a number from 0 to 999999 indicating which microsecond
    of the second it falls in.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type TIME, TIMESTAMP, NANOTIME or NANOTIMESTAMP.
    """
    ...


@builtin_function(_mifirstNot)
def mifirstNot(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Return the index of the first non-null element of X in a sliding window (based
    on the number of elements or time).

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_migrate)
def migrate(backupDir: Constant, backupDBPath: Constant = DFLT, backupTableName: Constant = DFLT, newDBPath: Constant = DFLT, newTableName: Constant = DFLT, keyPath: Constant = DFLT) -> Constant:
    r"""Restore the backup. It returns a table containing the restored data of each
    table. It must be executed by a logged-in user.

    The migrate function has the following 3 usages:

    - migrate(backupDir): Restore the backup of all databases in this directory. The
      restored database name and table name are the same as the original ones.

    - migrate(backupDir, backupDBPath): Restore the backup of the specified database
      in this directory. The restored database name and table name are the same as the
      original ones.

    - migrate(backupDir, backupDBPath, backupTableName, [newDBPath], [newTableName]):
      Restore the backup of the specified table of the specified database in the directory.

      - If newDBPath and newTableName are not specified, the restored database name
        and table name are the same as the original ones.

      - If newDBPath and newTableName are specified, the restored database name and
        table name will be newDBPath and newTableName, respectively.

    Parameters
    ----------
    backupDir : Constant
        A string indicating the directory to save the backup.
    backupDBPath : Constant
        A string indicating the path of a database.
    backupTableName : Constant
        A string indicating a table name.
    newDBPath : Constant
        A string indicating the new database name. If not specified, the default value
        is backupDBPath. To specify the parameter, make sure that the storage engine
        of the backup database is the same as the engine of newDBPath, and the partitionScheme
        must be the same (except for VALUE). For a VALUE partitioned database, the
        partitioning scheme of the backup database must be a subset of that of the
        database to be restored.
    newTableName : Constant
        A string indicating the new table name. If not specified, the default value
        is backupTableName.
    keyPath : Constant, optional
        (Linux only) A STRING scalar that specifies the path to the key file used for
        restoring an encrypted backup. The key version used for restoring the data must
        match the version specified during the backup. Note that when restoring an
        encrypted table, both the backup table and the target table must use the same
        encryption mode (i.e., the same encryptMode parameter specified during table creation).
    """
    ...


@builtin_function(_milastNot)
def milastNot(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Return the index of the last non-null element of X in a sliding window (based
    on the number of elements or time).

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_millisecond)
def millisecond(X: Constant) -> Constant:
    r"""For each element in X, return a number from 0 to 999 indicating which millisecond
    of the second it falls in.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type TIME, TIMESTAMP, NANOTIME or NANOTIMESTAMP.
    """
    ...


@builtin_function(_mimax)
def mimax(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Return the position of the element with the largest value in X in a sliding window.
    If there are multiple elements with the identical largest value in a window, return
    the position of the first element from the left. Same as other aggregate functions,
    null values are ignored.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mimaxLast)
def mimaxLast(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Return the position of the element with the largest value in X in a sliding window.
    If there are multiple elements with the identical largest value in a window, return
    the position of the first element from the right. Same as other aggregate functions,
    null values are ignored.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mimin)
def mimin(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Return the position of the element with the smallest value in X in a sliding window.
    If there are multiple elements with the identical smallest value in a window, return
    the position of the first element from the left. Same as other aggregate functions,
    null values are ignored.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_miminLast)
def miminLast(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Return the position of the element with the smallest value in X in a sliding window.
    If there are multiple elements with the identical smallest value in a window, return
    the position of the first element from the right. Same as other aggregate functions,
    null values are ignored.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_min)
def min(X: Constant, Y: Constant = DFLT) -> Constant:
    r"""For one input (null values will not be compared with other elements):

    - If X is a vector, return the minimum in X.

    - If X is a matrix, return the minimum in each column of X and return a vector.

    - If X is a table, return the minimum in each column of X and return a table.

    For two inputs (null values will be compared with other elements):

    - If Y is a scalar, compare it with each element in X, replace the element in X with
      the smaller value.

    - If Y and X are of the same type and length, compare the corresponding elements of
      them and return a vector containing each smaller value.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    Y : Constant, optional
        A scalar, a vector of the same length as X or a matrix.
    """
    ...


@builtin_function(_minIgnoreNull)
def minIgnoreNull(X: Constant, Y: Constant) -> Constant:
    r"""A binary scalar function that returns the minimum by comparing X with Y.

    Difference between min and minIgnoreNull:

    - min: Null values are treated as the minimum value if nullAsMinValueForComparison=true,
      otherwise comparison involving null values returns NULL.

    - minIgnoreNull: Null values are ignored in comparison and non-null minimum is returned.
      If both elements in X and Y are null, NULL is returned. This function is not affected
      by configuration parameter nullAsMinValueForComparison.

    Parameters
    ----------
    X : Constant
        A numeric, LITERAL or TEMPORAL scalar, pair, vector or matrix.
    Y : Constant
        A numeric, LITERAL or TEMPORAL scalar, pair, vector or matrix.
    """
    ...


@builtin_function(_minute)
def minute(X: Constant) -> Constant:
    r"""Return the corresponding minute(s).

    Parameters
    ----------
    X : Constant
        An integer or temporal scalar/vector.
    """
    ...


@builtin_function(_minuteOfHour)
def minuteOfHour(X: Constant) -> Constant:
    r"""For each element in X, return a number from 0 to 59 indicating which minute
    of the hour it falls in.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type TIME, MINUTE, SECOND, DATETIME, TIMESTAMP, NANOTIME
        or NANOTIMESTAMP.
    """
    ...


@builtin_function(_mkurtosis)
def mkurtosis(X: Constant, window: Constant, biased: Constant = DFLT, minPeriods: Constant = DFLT) -> Constant:
    r"""Calculate the moving kurtosis of X in a sliding window.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    biased : Constant
        A Boolean value indicating whether the result is biased. The default value is
        true, meaning the bias is not corrected.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mlast)
def mlast(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Return the last element of X in a sliding window.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mlastNot)
def mlastNot(X: Constant, window: Constant, k: Constant = DFLT, minPeriods: Constant = DFLT) -> Constant:
    r"""If X is a vector:

    - If k is not specified, return the last element of X that is not null in a sliding
      window.

    - If k is specified, return the last element of X that is neither k nor null in
      the window.

    If X is a matrix or table, conduct the aforementioned calculation within each
    column of X. The result is a matrix or table.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    k : Constant, optional
        A numeric or string scalar indicating the value to be matched.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mmad)
def mmad(X: Constant, window: Constant, useMedian: Constant = DFLT, minPeriods: Constant = DFLT) -> Constant:
    r"""Calculate the average absolute deviation of X in a sliding window.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    useMedian : Constant
        A Boolean value. The default value is false and it returns the mean absolute
        deviation, otherwise returns the median absolute deviation.

        - mean absolute deviation: mean(abs(X - mean(X)))

        - median absolute deviation: med(abs(X - med(X)))
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mmax)
def mmax(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Calculate the moving maximums of X in a sliding window.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mmaxPositiveStreak)
def mmaxPositiveStreak(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Obtain the maximum value of the sum of consecutive positive numbers in X within
    a sliding window of given size (based on the number of elements).

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    """
    ...


@builtin_function(_mmed)
def mmed(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Calculate the moving median of X in a sliding window.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mmin)
def mmin(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Calculate the moving minimums of X in a sliding window.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mmse)
def mmse(Y: Constant, X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Return the coefficient estimates of X and mean square errors of an ordinary-
    least-squares regression of Y on X with intercept with a rolling window. The
    length of the window is given by the parameter window.

    The mean square error (MSE) is calculated with the following formula:

    .. math::
        \begin{align*}
        MSE &= \frac{1}{n}\sum_{i=1}^n\left(Y_i-\hat{Y}_i\right)^2
        \end{align*}

    Parameters
    ----------
    Y : Constant
        A vector indicating the dependent variable.
    X : Constant
        A vector indicating the independent variable.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the
        size of the sliding window. Note: The window size is capped at 102400 when
        m-functions are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).

    Returns
    -------
    Constant
        A tuple with 2 vectors. The first vector is the coefficient estimates and
        the second vector is the mean square errors. Each vector is of the same length
        as X and Y.
    """
    ...


@builtin_function(_mod)
def mod(X: Constant, Y: Constant) -> Constant:
    r"""Mod means modulus. It returns the element-by-element remainder of X divided by
    Y. When Y is a positive integer, the modulus is always non-negative, e.g., -10 %
    3 is 2. When Y is a negative integer, the modulus is always non-positive, e.g.,
    -10 % -3 is -1. mod is often used to group data. For example, [5,4,3,3,5,6]%3 is
    [2,1,0,0,2,0]; data can thereby be divided into three groups.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix.
    Y : Constant
        A scalar/pair/vector/matrix. If X or Y is a pair/vector/matrix, the other is
        a scalar or a pair/vector/matrix of the same size.
    """
    ...


@builtin_function(_mode)
def mode(X: Constant) -> Constant:
    r"""If X is a vector, calculate the most frequently occurring value in X.

    If X is a matrix/table, calculate the most frequently occurring value in each
    column of X and return a vector/table.

    This function counts the occurrences of unique values (keys) in X using a hash
    table. If there are multiple keys with the highest count, the function returns
    the first key in the hash table. Note that the hash algorithm used by this function
    varies for different data types, so the output results may differ.

    As with all aggregate functions, null values are not included in the calculation.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_month)
def month(X: Constant) -> Constant:
    r"""Return the corresponding month(s).

    Parameters
    ----------
    X : Constant
        A temporal scalar/vector.
    """
    ...


@builtin_function(_monthBegin)
def monthBegin(X: Constant, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""Return the first day of the month that X belongs to.

    If parameter offset is specified, the result is updated every n months. The parameters
    offset and n must be specified together, and offset takes effect only when n > 1.

    Parameters
    ----------
    X : Constant
        A scalar/vector of data type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    offset : Constant
        A scalar of the same data type as X. It must be no greater than the minimum
        value of X. The default value is the minimum value of X.
    n : Constant
        A positive integer. The default value is 1.
    """
    ...


@builtin_function(_monthEnd)
def monthEnd(X: Constant, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""Return the last day of the month that X belongs to.

    If parameter offset is specified, the result is updated every n months. The parameters
    offset and n must be specified together, and offset takes effect only when n > 1.

    Parameters
    ----------
    X : Constant
        A scalar/vector of data type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    offset : Constant
        A scalar of the same data type as X. It must be no greater than the minimum
        value of X. The default value is the minimum value of X.
    n : Constant
        A positive integer. The default value is 1.
    """
    ...


@builtin_function(_monthOfYear)
def monthOfYear(X: Constant) -> Constant:
    r"""For each element in X, return a number from 1 to 12 indicating which month of
    the year it falls in.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type DATE, MONTH, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    """
    ...


@builtin_function(_move)
def move(X: Constant, steps: Constant) -> Constant:
    r"""move is the general form of prev and next.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    steps : Constant
        An integer indicating how many positions to shift the elements of X.

        - If steps is positive, X is moved to the right for steps positions;

        - If steps is negative, X is moved to the left for steps positions;

        - If steps is 0, X does not move;

        - If steps is a DURATION, X must be an indexed matrix or indexed series with
          temporal values as its row index.
    """
    ...


@builtin_function(_moveHotDataToColdVolume)
def moveHotDataToColdVolume(checkRange: Constant = DFLT, force: Constant = DFLT) -> Constant:
    r"""Migrate the specified data to coldVolumes.

    Parameters
    ----------
    checkRange : Constant
        An integer indicating the time range (in hours). The default value is 240, i.e.,
        10 days. If the parameter is specified, data within the range of [current
        time-hoursToColdVolumes-checkRange, current time-hoursToColdVolumes) will be
        migrated to coldVolumes.
    """
    ...


@builtin_function(_moving)
def moving(func: Constant, funcArgs: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Apply the function/operator to a moving window of the given objects.

    The moving template always returns a vector with the same number of elements as
    the number of rows in the input arguments. It starts calculating when the moving
    window size is reached for the first time, and the moving window is always shifted
    by 1 element to the right thereafter.

    Each of the built-in moving functions such as msum, mcount and mavg is optimized for
    its specific task. Therefore, they have much better performance than the moving template.

    Parameters
    ----------
    func : Constant
        An aggregate function.

        .. note::

            When using this parameter, the keyword used to define the corresponding
            aggregation function is defg. For details, refer to Tutorial: User Defined
            Aggregate Functions.

    funcArgs : Constant
        The parameters of func. They can be vectors/dictionaries/tables/matrices. It
        is a tuple if there are more than one parameter of func, and all parameters
        must have the same size.
    window : Constant
        The moving window size.
    minPeriods : Constant
        A positive integer indicating the minimum number of observations in a window
        in order to generate a result. The default value is the value of window.
    """
    ...


@builtin_function(_movingTopNIndex)
def movingTopNIndex(X: Constant, window: Constant, top: Constant, ascending: Constant = DFLT, fixed: Constant = DFLT, tiesMethod: Constant = DFLT) -> Constant:
    r"""Return an array vector indicating the indices of the first top elements of X
    after sorted within each sliding window.

    Parameters
    ----------
    X : Constant
        A numeric/temporal vector.
    window : Constant
        An integer no less than 2, indicating the window size.
    top : Constant
        An integer greater than 1 and no greater than window.
    ascending : Constant
        A Boolean value indicating whether the data within a window is sorted in
        ascending order. True means ascending order and false means descending order.
    fixed : Constant
        A Boolean value, indicating whether the length of each row in the output array
        vector is fixed to be top. The default value is false. When fixed = true, all
        rows are of the same length. For the first (top - 1) windows, the indices of
        missing elements are replaced with null values.
    tiesMethod : Constant
        A string that specifies how to select elements if there are more elements with
        the same value than spots available in the top N after sorting X within a
        sliding window. It can be:

        - 'oldest': select elements starting from the earliest entry into the window;

        - 'latest': select elements starting from the latest entry into the window.
    """
    ...


@builtin_function(_movingWindowIndex)
def movingWindowIndex(X: Constant, window: Constant, fixed: Constant = DFLT) -> Constant:
    r"""Return an array vector indicating the indices of the elements of X within each
    sliding window.

    Parameters
    ----------
    X : Constant
        A vector.
    window : Constant
        An integer no less than 2 indicating the window size.
    fixed : Constant
        A Boolean value, indicating whether the length of each row in the output array
        vector is fixed to be window. The default value is false. When fixed = true,
        all rows are of the same length. For the first (window - 1) windows, the indices
        of missing elements are filled with null values.
    """
    ...


@builtin_function(_mpercentile)
def mpercentile(X: Constant, percent: Constant, window: Constant, interpolation: Constant = DFLT, minPeriods: Constant = DFLT) -> Constant:
    r"""Return the percentile rank of each element of X in a sliding window.

    Parameters
    ----------
    percent : Constant
        An integer or floating value between 0 and 100.
    interpolation : Constant
        A string indicating the interpolation method to use if the specified percentile
        is between two elements in X (assuming the :math:`i^{th}` and :math:`(i+1)^{th}`
        element in the sorted X) . It can take the following values:

        - 'linear'(default): Return :math:`X_i+(X_i+1-X_1)*fraction`, where
          :math:`fraction = \frac{\tfrac{percentile}{100} - \tfrac{i}{size - 1}}{\tfrac{1}{size - 1}}`

        - 'lower': Return :math:`X_i`

        - 'higher': Return :math:`X_{i+1}`

        - 'nearest': Return :math:`X_i` that is closest to the specified percentile

        - 'midpoint': Return :math:`X_i`
    minPeriods : Constant
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mpercentileTopN)
def mpercentileTopN(X: Constant, S: Constant, percent: Constant, window: Constant, top: Constant, interpolation: Constant = DFLT, ascending: Constant = DFLT, tiesMethod: Constant = DFLT) -> Constant:
    r"""- When X is a vector, within a sliding window of given length (measured by the
      number of elements), the function stably sorts X by S in the order specified by
      ascending, then calculates the moving percentile rank of the first top elements.

    - When X is a matrix or table, conduct the aforementioned calculation within each
      column of X. The result is a matrix/table with the same shape as X.

    Parameters
    ----------
    X : Constant
        A numeric vector, matrix or table.
    S : Constant
        A numeric/temporal vector, matrix or table, based on which X are sorted.
    percent : Constant
        An integer or floating value between 0 and 100.
    interpolation : Constant, optional
        A string indicating the interpolation method to use if the specified percentile
        is between two elements in X (assuming the :math:`i^{th}` and :math:`(i+1)^{th}` element in the sorted X).
        It can take the following values:

        - 'linear'(default): Return :math:`X_i+(X_{i+1}-X_i) * fraction`, where
          :math:`fraction=\frac{percentile/100-i/(size-1)}{1/(size-1)}`

        - 'lower': Return :math:`X_i`

        - 'higher': Return :math:`X_{i+1}`

        - 'nearest': Return :math:`X_{i+1}` or :math:`X_i` that is closest to the specified percentile

        - 'midpoint': Return :math:`X_i`
    """
    ...


@builtin_function(_mprod)
def mprod(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Calculate the moving products of X in a sliding window.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mr)
def mr(ds: Constant, mapFunc: Constant, reduceFunc: Constant = DFLT, finalFunc: Constant = DFLT, parallel: Constant = DFLT) -> Constant:
    r"""The Map-Reduce function is the core function of DolphinDB's generic distributed
    computing framework.

    Parameters
    ----------
    ds : Constant
        The list of data sources. This required parameter must be a tuple and each
        element of the tuple is a data source object. Even if there is only one data
        source, we still need a tuple to wrap the data source.
    mapFunc : Constant
        The map function. It accepts one and only one argument, which is the materialized
        data entity from a data source. If we would like the map function to accept
        more parameters in addition to the materialized data source, we can use a
        PartialApplication to convert a multiple-parameter function to a unary function.
        The number of map function calls is the same as the number of data sources. The
        map function returns a regular object (scalar, pair, array, matrix, table, set,
        or dictionary) or a tuple (containing multiple regular objects).
    reduceFunc : Constant, optional
        The binary reduce function that combines two map function call results. The
        reduce function in most cases is trivial. An example is the addition function.
        The reduce function is optional. If the reduce function is not specified, the
        system returns all individual map call results to the final function.
    finalFunc : Constant, optional
        The final function which accepts one and only one parameter. The output of the
        last reduce function call is the input of the final function. If it is not
        specified, the system returns the individual map function call results.
    parallel : Constant, optional
        A boolean flag indicating whether to execute the map function in parallel locally.
        The default value is true, i.e., enabling parallel computing. When there is very
        limited available memory and each map call needs a large amount of memory, we
        can disable parallel computing to prevent the out-of-memory problem. We may also
        want to disable the parallel option in other scenarios. For example, we may need
        to disable the parallel option to prevent multiple threads from writing to the
        same partition simultaneously.
    """
    ...


@builtin_function(_mrank)
def mrank(X: Constant, ascending: Constant, window: Constant, ignoreNA: Constant = DFLT, tiesMethod: Constant = DFLT, percent: Constant = DFLT, minPeriods: Constant = DFLT) -> Constant:
    r"""Return the rank of each element of X in a sliding window.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    ascending : Constant
        A Boolean value indicating whether the sorting direction is ascending.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    ignoreNA : Constant
        A Boolean value indicating whether null values are ignored in ranking. The default
        value is true. If null values participate in the ranking, they are ranked the lowest.
    tiesMethod : Constant
        A string indicating how to rank the group of records with the same value (i.e., ties):

        - 'min': lowest rank of the group

        - 'max': highest rank of the group

        - 'average': average rank of the group
    percent : Constant
        A Boolean value, indicating whether to display the returned rankings in percentile
        form. The default value is false.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mskew)
def mskew(X: Constant, window: Constant, biased: Constant = DFLT, minPeriods: Constant = DFLT) -> Constant:
    r"""Calculate the moving skewness of X in a sliding window.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    biased : Constant
        A Boolean value indicating whether the result is biased. The default value is
        true, meaning the bias is not corrected.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mslr)
def mslr(Y: Constant, X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Conduct the simple least-squares regressions of Y on X in a sliding window.

    Parameters
    ----------
    Y : Constant
        A vector indicating the dependent variable.
    X : Constant
        A vector indicating the independent variable.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).

    Returns
    -------
    Constant
        A tuple of two vectors. The first vector is the intercepts and the second
        vector is the coefficient estimates of X.
    """
    ...


@builtin_function(_mstd)
def mstd(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Calculate the standard deviation of X in a sliding window.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mstdTopN)
def mstdTopN(X: Constant, S: Constant, window: Constant, top: Constant, ascending: Constant = DFLT, tiesMethod: Constant = DFLT) -> Constant:
    r"""Within a sliding window of given length (measured by the number of elements), the
    function stably sorts X by S in the order specified by ascending, then calculates
    the unbiased sample standard deviation of the first top elements.

    Parameters
    ----------
    X : Constant
        A numeric vector or matrix.
    S : Constant
        A numeric/temporal vector or matrix, based on which X are sorted.
    window : Constant
        An integer greater than 1, indicating the sliding window size.
    top : Constant
        An integer in (1, window], indicating the first top elements of X after sorted
        based on S.
    ascending : Constant, optional
        A Boolean value indicating whether to sort S in ascending order. The default
        value is true.
    tiesMethod : Constant, optional
        A string that specifies how to select elements if there are more elements with
        the same value than spots available in the top N after sorting X within a sliding
        window. It can be:

        - 'oldest': select elements starting from the earliest entry into the window;

        - 'latest': select elements starting from the latest entry into the window;

        - 'all': select all elements.

        .. note::

            For backward compatibility, the default value of tiesMethod is 'oldest' for
            the following functions: mstdTopN, mstdpTopN, mvarTopN, mvarpTopN, msumTopN,
            mavgTopN, mwsumTopN, mbetaTopN, mcorrTopN, mcovarTopN; For the remaining mTopN
            functions, the default value of tiesMethod is 'latest'.
    """
    ...


@builtin_function(_mstdp)
def mstdp(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Calculate the population standard deviation of X in a sliding window.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mstdpTopN)
def mstdpTopN(X: Constant, S: Constant, window: Constant, top: Constant, ascending: Constant = DFLT, tiesMethod: Constant = DFLT) -> Constant:
    r"""Within a sliding window of given length (measured by the number of elements), the
    function stably sorts X by S in the order specified by ascending, then calculates
    the population standard deviation of the first top elements.

    Parameters
    ----------
    X : Constant
        A numeric vector or matrix.
    S : Constant
        A numeric/temporal vector or matrix, based on which X are sorted.
    window : Constant
        An integer greater than 1, indicating the sliding window size.
    top : Constant
        An integer in (1, window], indicating the first top elements of X after sorted
        based on S.
    ascending : Constant, optional
        A Boolean value indicating whether to sort S in ascending order. The default
        value is true.
    tiesMethod : Constant, optional
        A string that specifies how to select elements if there are more elements with
        the same value than spots available in the top N after sorting X within a sliding
        window. It can be:

        - 'oldest': select elements starting from the earliest entry into the window;

        - 'latest': select elements starting from the latest entry into the window;

        - 'all': select all elements.

        .. note::

            For backward compatibility, the default value of tiesMethod is 'oldest' for
            the following functions: mstdTopN, mstdpTopN, mvarTopN, mvarpTopN, msumTopN,
            mavgTopN, mwsumTopN, mbetaTopN, mcorrTopN, mcovarTopN; For the remaining mTopN
            functions, the default value of tiesMethod is 'latest'.
    """
    ...


@builtin_function(_msum)
def msum(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Calculate the moving sum of X in a sliding window.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_msum2)
def msum2(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Calculate the sum of squares of all elements of X in a sliding window (based on
    the number of elements or time). Please note that the return is always of DOUBLE type.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_msumTopN)
def msumTopN(X: Constant, S: Constant, window: Constant, top: Constant, ascending: Constant = DFLT, tiesMethod: Constant = DFLT) -> Constant:
    r"""Within a sliding window of given length (measured by the number of elements), the
    function stably sorts X by S in the order specified by ascending, then sums up the
    first top elements.

    Parameters
    ----------
    X : Constant
        A numeric vector or matrix.
    S : Constant
        A numeric/temporal vector or matrix, based on which X are sorted.
    window : Constant
        An integer greater than 1, indicating the sliding window size.
    top : Constant
        An integer in (1, window], indicating the first top elements of X after sorted
        based on S.
    ascending : Constant, optional
        A Boolean value indicating whether to sort S in ascending order. The default
        value is true.
    tiesMethod : Constant, optional
        A string that specifies how to select elements if there are more elements with
        the same value than spots available in the top N after sorting X within a sliding
        window. It can be:

        - 'oldest': select elements starting from the earliest entry into the window;

        - 'latest': select elements starting from the latest entry into the window;

        - 'all': select all elements.

        .. note::

            For backward compatibility, the default value of tiesMethod is 'oldest' for
            the following functions: mstdTopN, mstdpTopN, mvarTopN, mvarpTopN, msumTopN,
            mavgTopN, mwsumTopN, mbetaTopN, mcorrTopN, mcovarTopN; For the remaining mTopN
            functions, the default value of tiesMethod is 'latest'.
    """
    ...


@builtin_function(_mul)
def mul(X: Constant, Y: Constant) -> Constant:
    r"""Return the element-by-element product of X and Y.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix.
    Y : Constant
        A scalar/pair/vector/matrix. If one of X and Y is a pair/vector/matrix, the
        other must be a scalar or a pair/vector/matrix of the same size.
    """
    ...


@builtin_function(_multiTableRepartitionDS)
def multiTableRepartitionDS(query: Constant, column: Constant = DFLT, partitionType: Constant = DFLT, partitionScheme: Constant = DFLT, local: Constant = DFLT) -> Constant:
    r"""Generate a tuple of data sources from multiple tables with a new partitioning design.

    If query is metacode of SQL statements, the parameter column must be specified.
    partitionType and partitionScheme can be unspecified for a partitioned table with a
    COMPO domain. In this case, the data sources will be determined based on the original
    partitionType and partitionScheme of column.

    If query is a tuple of metacode of SQL statements, column, partitionType and partitionScheme
    should be unspecified. The function returns a tuple with the same length as query. Each
    element of the result is a data source corresponding to a piece of metacode in query.

    Parameters
    ----------
    query : Constant
        Metacode of SQL statements or a tuple of metacode of SQL statements.
    column : Constant
        A string indicating a column name in query. Function multiTableRepartitionDS
        deliminates data sources based on column.
    partitionType : Constant
        The type of partition. It can take the value of VALUE or RANGE.
    partitionScheme : Constant
        A vector indicating the partitioning scheme. For details please refer to DistributedComputing.
    local : Constant
        A Boolean value indicating whether to move the data sources to the local node
        for computing. The default value is true.
    """
    ...


@builtin_function(_multinomialNB)
def multinomialNB(Y: Constant, X: Constant, varSmoothing: Constant = DFLT) -> Constant:
    r"""Conduct the multinomial Naive Bayesian classification.

    Parameters
    ----------
    Y : Constant
        A vector with the same length as table X. Each element of labels indicates
        the class that the correponding row in X belongs to.
    X : Constant
        A table indicating the training set. Each row is a sample and each column is
        a feature.
    varSmoothing : Constant
        A positive floating number between 0 and 1 indicating the additive (Laplace/
        Lidstone) smoothing parameter (0 for no smoothing).

    Returns
    -------
    Constant
        A dictionary with the following keys:

        - model: a RESOURCE data type variable. It is an internal binary resource
          generated by function multinomialNB and to be used by function predict.

        - modelName: string "multinomialNB".

        - varSmoothing: varSmoothing parameter value.
    """
    ...


@builtin_function(_mutualInfo)
def mutualInfo(X: Constant, Y: Constant) -> Constant:
    r"""Calculate the mutual information of X and Y.

    The calculation uses the following formula:

    :math:`MI(U,V) =  \sum\limits_{i = 1}^{|U|}\sum\limits_{j = 1}^{|V|}\dfrac{|{U_i} \cap {V_j}|}{N}log \dfrac{N\lvert{U_i} \cap {V_i}\rvert}{|U_i||V_j|}`

    If X or Y is a matrix, calculate the mutual information of each column and return
    a vector.

    Please note that the natural logarithm is used in this formula. If base is set to
    2 or 10, please divide the result by log 2 or log 10.

    Parameters
    ----------
    X : Constant
        A scalar/vector/ matrix.
    Y : Constant
        A scalar/vector/ matrix. X and Y can be integral or symbol types.
    """
    ...


@builtin_function(_mvar)
def mvar(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Calculate the moving variances of X in a sliding window.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mvarTopN)
def mvarTopN(X: Constant, S: Constant, window: Constant, top: Constant, ascending: Constant = DFLT, tiesMethod: Constant = DFLT) -> Constant:
    r"""Within a sliding window of given length (measured by the number of elements), the
    function stably sorts X by S in the order specified by ascending, then calculates
    the unbiased sample variance of the first top elements.

    Parameters
    ----------
    X : Constant
        A numeric vector or matrix.
    S : Constant
        A numeric/temporal vector or matrix, based on which X are sorted.
    window : Constant
        An integer greater than 1, indicating the sliding window size.
    top : Constant
        An integer in (1, window], indicating the first top elements of X after sorted
        based on S.
    ascending : Constant, optional
        A Boolean value indicating whether to sort S in ascending order. The default
        value is true.
    tiesMethod : Constant, optional
        A string that specifies how to select elements if there are more elements with
        the same value than spots available in the top N after sorting X within a sliding
        window. It can be:

        - 'oldest': select elements starting from the earliest entry into the window;

        - 'latest': select elements starting from the latest entry into the window;

        - 'all': select all elements.

        .. note::

            For backward compatibility, the default value of tiesMethod is 'oldest' for
            the following functions: mstdTopN, mstdpTopN, mvarTopN, mvarpTopN, msumTopN,
            mavgTopN, mwsumTopN, mbetaTopN, mcorrTopN, mcovarTopN; For the remaining mTopN
            functions, the default value of tiesMethod is 'latest'.
    """
    ...


@builtin_function(_mvarp)
def mvarp(X: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Calculate the moving population variances of X in a sliding window.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mvarpTopN)
def mvarpTopN(X: Constant, S: Constant, window: Constant, top: Constant, ascending: Constant = DFLT, tiesMethod: Constant = DFLT) -> Constant:
    r"""Within a sliding window of given length (measured by the number of elements), the
    function stably sorts X by S in the order specified by ascending, then calculates
    the population variance of the first top elements.

    Parameters
    ----------
    X : Constant
        A numeric vector or matrix.
    S : Constant
        A numeric/temporal vector or matrix, based on which X are sorted.
    window : Constant
        An integer greater than 1, indicating the sliding window size.
    top : Constant
        An integer in (1, window], indicating the first top elements of X after sorted
        based on S.
    ascending : Constant, optional
        A Boolean value indicating whether to sort S in ascending order. The default
        value is true.
    tiesMethod : Constant, optional
        A string that specifies how to select elements if there are more elements with
        the same value than spots available in the top N after sorting X within a sliding
        window. It can be:

        - 'oldest': select elements starting from the earliest entry into the window;

        - 'latest': select elements starting from the latest entry into the window;

        - 'all': select all elements.

        .. note::

            For backward compatibility, the default value of tiesMethod is 'oldest' for
            the following functions: mstdTopN, mstdpTopN, mvarTopN, mvarpTopN, msumTopN,
            mavgTopN, mwsumTopN, mbetaTopN, mcorrTopN, mcovarTopN; For the remaining mTopN
            functions, the default value of tiesMethod is 'latest'.
    """
    ...


@builtin_function(_mwavg)
def mwavg(X: Constant, Y: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Calculate the moving averages of X with Y as weights in a sliding window.

    .. note::

        Different from mavg that is based on a window of size (weight) length, mwavg
        must use X and Y of the same length.

    The weights in a rolling window are automatically adjusted so that the sum of
    weights for all non-null elements in the rolling window is 1.

    Parameters
    ----------
    Y : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mwsum)
def mwsum(X: Constant, Y: Constant, window: Constant, minPeriods: Constant = DFLT) -> Constant:
    r"""Calculate the moving sums of X with Y as weights in a sliding window.

    The weights in a rolling window are automatically adjusted so that the sum of
    weights for all non-null elements in the rolling window is 1.

    Parameters
    ----------
    Y : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    X : Constant
        A vector/matrix/table/tuple (with scalars or equal-length vectors)/dictionary.
    window : Constant
        An integer no smaller than 2 or a scalar of DURATION type indicating the size
        of the sliding window. Note: The window size is capped at 102400 when m-functions
        are used in the streaming engines.
    minPeriods : Constant, optional
        A positive integer indicating the minimum number of observations in a window
        required to be not null (otherwise the result is NULL).
    """
    ...


@builtin_function(_mwsumTopN)
def mwsumTopN(X: Constant, Y: Constant, S: Constant, window: Constant, top: Constant, ascending: Constant = DFLT, tiesMethod: Constant = DFLT) -> Constant:
    r"""Within a sliding window of given length (measured by the number of elements),
    the function stably sorts X and Y by S in the order specified by ascending, then
    calculates the moving sums of X with Y as weights.

    Parameters
    ----------
    X : Constant
        A numeric vector or matrix.
    Y : Constant
        A numeric vector or matrix.
    S : Constant
        A numeric/temporal vector or matrix, based on which X are sorted.
    window : Constant
        An integer greater than 1, indicating the sliding window size.
    top : Constant
        An integer in (1, window], indicating the first top elements of X after sorted
        based on S.
    ascending : Constant, optional
        A Boolean value indicating whether to sort S in ascending order. The default
        value is true.
    tiesMethod : Constant, optional
        A string that specifies how to select elements if there are more elements with
        the same value than spots available in the top N after sorting X within a sliding
        window. It can be:

        - 'oldest': select elements starting from the earliest entry into the window;

        - 'latest': select elements starting from the latest entry into the window;

        - 'all': select all elements.

        .. note::

            For backward compatibility, the default value of tiesMethod is 'oldest' for
            the following functions: mstdTopN, mstdpTopN, mvarTopN, mvarpTopN, msumTopN,
            mavgTopN, mwsumTopN, mbetaTopN, mcorrTopN, mcovarTopN; For the remaining mTopN
            functions, the default value of tiesMethod is 'latest'.
    """
    ...


@builtin_function(_nanInfFill)
def nanInfFill(X: Constant, Y: Constant) -> Constant:
    r"""In DolphinDB, NaN and Inf values of floating-point numbers are replaced with null values.
    Nan and Inf values can arise in the course of data import, or during calculations
    involving external data sources.

    This function replaces the NaN/Inf value in X with the specified Y.

    .. note::

        When X is a dictionary, only dictionary values are replaced.
    """
    ...


@builtin_function(_nanosecond)
def nanosecond(X: Constant) -> Constant:
    r"""For each element in X, return a number indicating which nanosecond of the second it falls in.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type TIME, TIMESTAMP, NANOTIME or NANOTIMESTAMP.
    """
    ...


@builtin_function(_nanotime)
def nanotime(X: Constant) -> Constant:
    r"""Convert the data type of X to NANOTIME.

    Parameters
    ----------
    X : Constant
        An integer or temporal scalar/vector.
    """
    ...


@builtin_function(_nanotimestamp)
def nanotimestamp(X: Constant) -> Constant:
    r"""Convert the data type of X to NANOTIMESTAMP. If there is no date in the argument X,
    return a timestamp from 1970.01.01 00:00:00.000000000 + X (nanoseconds).

    Parameters
    ----------
    X : Constant
        An integer or temporal scalar/vector.
    """
    ...


@builtin_function(_ne)
def ne(X: Constant, Y: Constant) -> Constant:
    r"""If neither X nor Y is a set, conduct the element-by-element comparison of X and Y;
    return 1 if the elements in X and Y are not the same.

    If both X and Y are sets, check if X and Y are not identical.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix/set.
    Y : Constant
        A scalar/pair/vector/matrix/set.
    """
    ...


@builtin_function(_neg)
def neg(X: Constant) -> Constant:
    r"""Return the negative of X.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix.
    """
    ...


@builtin_function(_neville)
def neville(X: Constant, Y: Constant, resampleRule: Constant, closed: Constant = DFLT, origin: Constant = DFLT, outputX: Constant = DFLT) -> Constant:
    r"""Resample X based on the specified resampleRule, closed and origin.
    Perform neville interpolation on Y based on the resampled X.

    If outputX is unspecified, return a vector of Y after the interpolation.

    If outputX=true, return a tuple where the first element is the vector of
    resampled X and the second element is a vector of Y after the interpolation.

    Parameters
    ----------
    X : Constant
        A strictly increasing vector of temporal type.
    Y : Constant
        A numeric vector of the same length as X.
    resampleRule : Constant
        A string. See the parameter rule of function resample for the optional values.
    closed : Constant, optional
        A string indicating which boundary of the interval is closed.

        - The default value is 'left' for all values of rule except for 'M', 'A',
          'Q', 'BM', 'BA', 'BQ', and 'W' which all have a default of 'right'.

        - The default is 'right' if origin is 'end' or 'end_day'.
    origin : Constant, optional
        A string indicating which boundary is used to label the interval.

        - The default value is 'left' for all values of rule except for 'M', 'A',
          'Q', 'BM', 'BA', 'BQ', and 'W' which all have a default of 'right'.

        - The default is 'right' if origin is 'end' or 'end_day'.
    outputX : Constant, optional
        A Boolean value indicating whether to output the resampled X. The default value is false.
    """
    ...


@builtin_function(_next)
def next(X: Constant) -> Constant:
    r"""Shift the elements of a vector to the left for one position. In comparison,
    prev shifts the elements of a vector to the right for one position; move shifts
    the elements of a vector for multiple positions.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    """
    ...


@builtin_function(_nextState)
def nextState(X: Constant) -> Constant:
    r"""Consecutive elements in X with the same value feature the same state, and
    a null value has no state. The state of each element is equal to its value.
    Return the next state of the current state for each element in X.
    If it is null, return the next adjacent state.

    If X is a matrix, return the next state for each column of the matrix.

    Parameters
    ----------
    X : Constant
        A vector or matrix of temporal/Boolean/numeric type.
    """
    ...


@builtin_function(_norm)
def norm(mean: Constant, std: Constant, count: Constant) -> Constant:
    r"""Return a vector (matrix) that follows a normal distribution.

    Parameters
    ----------
    mean : Constant
        A numeric scalar indicating the mean of a normal distribution.
    std : Constant
        A numeric scalar indicating standard deviation of a normal distribution.
    count : Constant
        An integral scalar/pair. A scalar indicates the length of the output vector. A pair indicates the dimension of the output matrix.
    """
    ...


@builtin_function(_normal)
def normal(mean: Constant, std: Constant, count: Constant) -> Constant:
    r"""Alias for norm. Return a vector (matrix) that follows a normal distribution.

    Parameters
    ----------
    mean : Constant
        A numeric scalar indicating the mean of a normal distribution.
    std : Constant
        A numeric scalar indicating standard deviation of a normal distribution.
    count : Constant
        An integral scalar/pair. A scalar indicates the length of the output vector. A pair indicates the dimension of the output matrix.
    """
    ...


@builtin_function(_not)
def Not(X: Constant) -> Constant:
    r"""Return NOT of each element of X. Returned values are 0, 1, or null. NOT of 0 is 1;
    NOT of null is still null; NOT of all other values is 0.

    Parameters
    ----------
    X : Constant
        Ascalar/pair/vector/matrix.
    """
    ...


@builtin_function(_now)
def now(nanoSecond: Constant = DFLT) -> Constant:
    r"""Return the current timestamp.

    .. note::

        Nanosecond precision may not be supported on certain versions of Windows.
        Therefore, even if nanoSecond=true is specified, it may still return timestamps
        with millisecond precision.

    Parameters
    ----------
    nanoSecond : Constant, optional
        A Boolean value indicating whether to display the result with nanosecond precision.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_ns)
    def ns(maturity: Constant, yield_: Constant, method: Constant = DFLT, maxIter: Constant = DFLT, bounds: Constant = DFLT, initialGuess: Constant = DFLT, seed: Constant = DFLT) -> Constant:
        r"""Fit yield curve using NS (Nelson-Siegel) model.

        Parameters
        ----------
        maturity : Constant
            _description_
        yield_ : Constant
            _description_
        method : Constant, optional
            _description_, by default DFLT
        maxIter : Constant, optional
            _description_, by default DFLT
        bounds : Constant, optional
            _description_, by default DFLT
        initialGuess : Constant, optional
            _description_, by default DFLT
        seed : Constant, optional
            _description_, by default DFLT

        Returns
        -------
        Constant
            A dictionary with the following keys:

            - modelName: The model used.

              - params: The fitted model parameters.

              - NS model: a vector of length 4, containing β0, β1, β2, λ.

              - NSS model: a vector of length 6, containing β0, β1, β2, β3, λ0, λ1.

            - fminResult: The optimization result.

              - 'nm' : See fmin.

              - 'bfgs': See fminBFGS.

              - 'lbfgs': See fminLBFGSB.

              - 'slsqp': See fminSLSQP.

              - 'de': See differentialEvolution.

            - predict: The prediction function of the model, which returns the
              predicted yield with this model. It can be called using model.
              predict(T) or predict(model, T), where T is the maturity in years.
        """
        ...


if not sw_is_ce_edition():
    @builtin_function(_nss)
    def nss(maturity: Constant, yield_: Constant, method: Constant = DFLT, maxIter: Constant = DFLT, bounds: Constant = DFLT, initialGuess: Constant = DFLT, seed: Constant = DFLT) -> Constant:
        r"""Fit yield curve using NSS (Nelson-Siegel-Svensson) model.

        Parameters
        ----------
        maturity : Constant
            _description_
        yield_ : Constant
            _description_
        method : Constant, optional
            _description_, by default DFLT
        maxIter : Constant, optional
            _description_, by default DFLT
        bounds : Constant, optional
            _description_, by default DFLT
        initialGuess : Constant, optional
            _description_, by default DFLT
        seed : Constant, optional
            _description_, by default DFLT

        Returns
        -------
        Constant
            A dictionary with the following keys:

            - modelName: The model used.

            - params: The fitted model parameters.

              - NS model: a vector of length 4, containing β0, β1, β2, λ.

              - NSS model: a vector of length 6, containing β0, β1, β2, β3, λ0, λ1.

            - fminResult: The optimization result.

              - 'nm' : See fmin.

              - 'bfgs': See fminBFGS.

              - 'lbfgs': See fminLBFGSB.

              - 'slsqp': See fminSLSQP.

              - 'de': See differentialEvolution.

            - predict: The prediction function of the model, which returns the
              predicted yield with this model. It can be called using model.
              predict(T) or predict(model, T), where T is the maturity in years.
        """
        ...


if not sw_is_ce_edition():
    @builtin_function(_nssPredict)
    def nssPredict(model: Constant, T: Constant) -> Constant:
        r"""Predict yield using the NS/NSS model.

        Parameters
        ----------
        model : Constant
            A dictionary with the following key-value pairs:

            - modelName: A string "ns" (Nelson-Siegel) or "nss" (Nelson-Siegel-Svensson).

            - params: A numeric vector indicating the fitted model parameters.

            - NS model: a vector of length 4, containing β0, β1, β2, λ.

            - NSS model: a vector of length 6, containing β0, β1, β2, β3, λ0, λ1.
        T : Constant
            A numeric vector with positive elements, indicating the maturity
            (in years) of a bond.
        """
        ...


@builtin_function(_nullCompare)
def nullCompare(func: Constant, X: Constant, Y: Constant) -> Constant:
    r"""Return a Boolean value which is the result of func(X,Y). Return NULL if
    the calculation involves null values. This function is not affected by the
    configuration paramter nullAsMinValueForComparison.

    Parameters
    ----------
    func : Constant
        The operator <, >, >=, <=, or the function between, in.
    X : Constant
        Can be a scalar, pair, vector, matrix, or set.
    Y : Constant
        Can be a scalar, pair, vector, matrix, or set.

        .. note::

            X and Y do not support the following data types currently: STRING,
            SYMBOL, IPADDR, UUID, BLOB, INT128.
    """
    ...


@builtin_function(_nullFill)
def nullFill(X: Constant, Y: Constant) -> Constant:
    r"""When X is a vector/matrix:

    - If Y is a scalar: replace the null values in X with Y.

    - If Y is a vector/matrix : replace the null values in X with the values of corresponding elements in Y.

    When X is a table, Y must be a scalar, and the function replaces all null values in X with Y. It is especially useful when we would like to replace all null values in a table with a certain value, such as -999999. Note that the system will convert the data type of Y to the specified column during the replacement. If Y cannot be converted, an error is raised.

    The function always returns a new object. Input X is not altered.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    Y : Constant
        Either a scalar, or a vector/matrix with the same dimension as X.
    """
    ...


@builtin_function(_nullFill_)
def nullFill_(X: Constant, Y: Constant) -> Constant:
    r"""Please refer to `nullFill`. The only difference between `nullFill` and `nullFill_`
    is that the latter assigns the result to X and thus changing the value of X after the execution.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    Y : Constant
        Either a scalar, or a vector/matrix with the same dimension as X.
    """
    ...


@builtin_function(_nullIf)
def nullIf(a: Constant, b: Constant) -> Constant:
    r"""- For two scalars, the function returns a null value if the values and
      data types of X and Y are equal. Otherwise, returns X.

    - For two vectors of equal length, the function conducts the aforementioned
      calculation with each pair of elements in X and Y at the same position.

    - For a scalar and a vector, the function conducts the aforementioned
      calculation on the scalar and each element of the vector.

    Parameters
    ----------
    a : Constant
        Can be a scalar or vector, or an expression that returns a scalar or vector.
    b : Constant
        Can be a scalar or vector, or an expression that returns a scalar or vector.
    """
    ...


@builtin_function(_nunique)
def nunique(X: Constant, ignoreNull: Constant = DFLT) -> Constant:
    r"""If X is a vector/array vector, return the number of unique elements in X.

    If X is a tuple, elements of each vector at the same position forms a key,
    and this function returns the number of unique keys.

    Parameters
    ----------
    X : Constant
        A vector/array vector or a tuple composed of multiple vectors with same length.
    ignoreNull : Constant, optional
        A Boolean value. If set to true, only non-null elements will be included
        in the calculation. The default value is false. Note that if X is a tuple
        or array vector, ignoreNull must be set to false.
    """
    ...


@builtin_function(_objByName)
def objByName(name: Constant, sharedVar: Constant = DFLT) -> Constant:
    r"""DolphinDB parses script before execution. The parsing procedure checks if
    a variable has been defined locally. If not, it will throw an exception.
    Assume we execute a locally defined function at remote nodes and the function
    queries a shared table that exists at remote nodes but not at the local node.
    If we directly call the table name in SQL statements, the system will fail to parse.

    To address this issue, we introduce function objByName which returns an object by name at runtime.

    If sharedVar is not specified, the system searches in local variables before
    searching in shared variables. If sharedVar = true, the system only searches
    in shared variables; if sharedVar = false, the system only searches in local variables.

    Parameters
    ----------
    name : Constant
        A  string indicating a table name.
    sharedVar : Constant, optional
        A Boolean value.
    """
    ...


@builtin_function(_objectChecksum)
def objectChecksum(vector: Constant, prev: Constant = DFLT) -> Constant:
    r"""Calculate the checksum of a vector. The result is an integer. It is often used to verify data integrity.

    Parameters
    ----------
    vector : Constant
        A vector that is used for calculating checksums.
    prev : Constant, optional
        An integer. If the vector is too long, the checksum can be computed
        iteratively by specifying prev which represents the checksum of the previous segment of data during iteration.
    """
    ...


@builtin_function(_objs)
def objs(shared: Constant = DFLT) -> Constant:
    r"""Obtain the information on the variables in memory. Return a table with the following columns:

    - name: variable name

    - type: data type

    - form: data form

    - rows:

      - If the data form is vector/dictionary/set, return the number of all elements (including null values);

      - If the data form is matrix/table, return the number of rows.

    - columns:

      - If the data form is vector/dictionary/set, return 1;

      - If the data form is matrix/table, return the number of columns.

    - bytes: the memory (in bytes) used by the variable

    - shared: whether it is a shared variable

    - extra: the logical path to the DFS table, in the format of "dfs://dbName/tableName"

    - owner: the creator of shared variables. This column will only be displayed
      when shared is set to true. It will be left empty for local variables.

    Please note that the function does not return the function definitions.
    You can use defs to check function definitions, or memSize for the memory usage.

    Parameters
    ----------
    shared : Constant, optional
        A Boolean variable.

        - false (default): return info on all variables in the current session

        - true: return info on all variables in the current session and variables
          shared by other sessions
    """
    ...


@builtin_function(_ols)
def ols(Y: Constant, X: Constant, intercept: Constant = DFLT, mode: Constant = DFLT, method: Constant = DFLT, usePinv: Constant = DFLT) -> Constant:
    r"""Return the result of an ordinary-least-squares regression of Y on X.

    Note that null values in X and Y are treated as 0 in calculations.

    Parameters
    ----------
    Y : Constant
        A vector indicating the dependent variable.
    X : Constant
        A  vector/matrix/table/tuple indicating the independent variable(s).
    intercept : Constant, optional
        A Boolean variable indicating whether the regression includes the intercept.
        If it is true, the system automatically adds a column of 1's to X to
        generate the intercept. The default value is true.
    mode : Constant, optional
        An integer indicating the contents in the output. It can be:

        - 0 (default): a vector of the coefficient estimates.

        - 1: a table with coefficient estimates, standard error, t-statistics, and p-values.

        - 2: a dictionary with the following keys: ANOVA, RegressionStat, Coefficient and Residual.

    method : Constant, optional
        A string indicating the method for the ordinary-least-squares regression problem.

        - When set to "default" (by default), ols solves the problem by constructing coefficient matrices and inverse matrices.

        - When set to "svd", ols solves the problem by using singular value decomposition.
    usePinv : Constant, optional
        A Boolean value indicating whether to use pseudo-inverse method to calculate inverse of a matrix.

        - true (default): computing the pseudo-inverse of the matrix. It must be true for singular matrices.

        - false: computing the inverse of the matrix, which is only applicable to non-singular matrices.
    """
    ...


@builtin_function(_olsEx)
def olsEx(ds: Constant, Y: Constant, X: Constant, intercept: Constant = DFLT, mode: Constant = DFLT) -> Constant:
    r"""Return the result of an ordinary-least-squares regression of Y on X. Y and X are columns in a partitioned table.

    Note that null values in X and Y are treated as 0 in calculations.

    Parameters
    ----------
    ds : Constant
        A set of data sources stored in a tuple. It is usually generated by the function sqlDS.
    Y : Constant
        A string indicating the column name of the dependent variable from the
        table represented by ds.
    X : Constant
        A string scalar/vector indicating the column name(s) of independent
        variable(s) from the table represented by ds.
    intercept : Constant, optional
        A boolean variable indicating whether the regression includes the intercept.
        If it is true, the system automatically adds a column of 1's to X to
        generate the intercept. The default value is true.
    mode : Constant, optional
        An integer that could be 0,1,2. It indicates the contents in the output.
        The default value is 0.

        - 0: a vector of the coefficient estimates

        - 1: a table with coefficient estimates, standard error, t-statistics, and p-value

        - 2: a dictionary with all statistics
    """
    ...


@builtin_function(_oneHot)
def oneHot(obj: Constant, encodingColumns: Constant) -> Constant:
    r"""Perform one-hot encoding on the specified columns in an in-memory table.
    It returns a table with columns in the order of encoded columns and non-encoded columns.
    The name of the encoded columns is "original column name_value".

    Parameters
    ----------
    obj : Constant
        An in-memory table.
    encodingColumns : Constant
        A STRING scalar or vector, indicating the columns for one-hot encoding.
    """
    ...


@builtin_function(_or)
def Or(X: Constant, Y: Constant) -> Constant:
    r"""Return the element-by-element logical X OR Y. If the operands contain null values, the operator || returns NULL.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix.
    Y : Constant
        A scalar/pair/vector/matrix.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_osqp)
    def osqp(q: Constant, P: Constant = DFLT, A: Constant = DFLT, l: Constant = DFLT, u: Constant = DFLT) -> Constant:
        r"""Solve the following optimization problem with a quadratic objective
        function and a set of linear constraints.

        .. math::

            \begin{align*}
            \min_{x}\ &\frac{1}{2}x^T P x + q^T x\\
            \text{subject to}\ &\; lb \le A x \le ub
            \end{align*}

        Parameters
        ----------
        q : Constant
            A vector indicating the linear coefficient of the objective function.
        P : Constant, optional
            A positive semi-definite matrix indicating the quadratic coefficients
            of the objective function.
        A : Constant, optional
            The coefficient matrix of linear inequality constraints.
        l : Constant, optional
            The left-hand-side vector of the linear inequality constraint.
        u : Constant, optional
            The right-hand-side vector of the linear inequality constraint.

        Returns
        -------
        Constant
            A 2-element tuple:

            - The first element is a string indicating the state of the solution:

              - solved: solution found;

              - solved inaccurate: solution found but the result is inaccurate;

              - primal infeasible: no feasible solution to the primal;

              - dual infeasible: no feasible solution to the dual;

              - maximum iterations reached: reach the maximum number of iterations;

              - run time limit reached: execution timeout;

              - problem non convex: the problem is non-convex;

              - interrupted: solution interrupted;

              - unsolved: solution not found.

            - The second element is the value of x where the value of the objective function is minimized.
        """
        ...


@builtin_function(_pack)
def pack(format: Constant, *args) -> Constant:
    r"""Return a bytes object packed according to the format string format.

    Parameters
    ----------
    format : Constant
        A format string.

        - A format character may be preceded by an integral repeat count. For example, the format string 4h means exactly the same as hhhh.

        - Whitespace characters between formats are ignored; a count and its format must not contain whitespace though.

        - For the s format character, the count is interpreted as the length of the bytes, not a repeat count like for the other format characters; for example, 10s means a single 10-byte string, while 10c means 10 characters. If a count is not given, it defaults to 1. The string is truncated or padded with null bytes as appropriate to make it fit.
    """
    ...


@builtin_function(_pair)
def pair(first: Constant, second: Constant) -> Constant:
    r"""Return a data pair.

    Parameters
    ----------
    first : Constant
        A scalar.
    second : Constant
        A scalar.

    Returns
    -------
    Constant
        A pair.
    """
    ...


@builtin_function(_panel)
def panel(row: Constant, col: Constant, metrics: Constant, rowLabel: Constant = DFLT, colLabel: Constant = DFLT, parallel: Constant = DFLT) -> Constant:
    r"""Rearrange metrics as a matrix (or multiple matrices). For each vector in metrics, return a matrix.

    Function panel is similar to SQL pivotBy clause in that they can both rearrange data as a matrix based on 2 dimensions. The difference is that exec... pivot by... can only convert one column into a matrix whereas function panel can convert one or multiple columns into one or multiple matrices.

    Parameters
    ----------
    row : Constant
        A vector. Each element corresponds to a row in a matrix in the result.
    col : Constant
        A vector. Each element corresponds to a column in a matrix in the result.
    metrics : Constant
        Oone or multiple vectors. Each vector in metrics corresponds to a matrix in the result.
    rowLabel : Constant, optional
        A vector of row labels for the matrix (or matrices) in the result. It is
        composed of distinct values in ascending order. The result only includes
        the rows specified in rowLabel.
    colLabel : Constant, optional
        A vector of column labels for the matrix (or matrices) in the result.
        It is composed of distinct values in ascending order. The result only
        includes the columns specified in colLabel.
    parallel : Constant, optional
        A Boolean value indicating whether to conduct parallel computing.
        The default value is false.
    """
    ...


@builtin_function(_parseExpr)
def parseExpr(X: Constant, varDict: Constant = DFLT, modules: Constant = DFLT, overloadedOperators: Constant = DFLT) -> Constant:
    r"""Convert string into metacode, which can be executed by function eval.

    Parameters
    ----------
    X : Constant
        A string scalar/vector.
    varDict : Constant, optional
        An optional parameter, which is a dictionary. If varDict is specified,
        while parsing by function eval , the variable in X will be parsed as the
        key of varDict. And the value of this variable is the value of varDict.
    modules : Constant, optional
        An optional parameter which can be a string or an array of strings,
        indicating the name of the module to be loaded.
    overloadedOperators : Constant, optional
        An optional parameter, which is a dictionary. The operators are mapped to
        a function. The key must be a string scalar, and the value must be a binary function.
    """
    ...


@builtin_function(_parseInt)
def parseInt(X: Constant, type: Constant, radix: Constant = DFLT) -> Constant:
    r"""parseInteger parses X into an integer of the specified type in specified radix.
    If it encounters a character that is not a numeral in the specified radix, it
    ignores it and all succeeding characters and returns the integer value parsed
    up to that point. An exception will be thrown if the first character is invalid.

    Parameters
    ----------
    X : Constant
        A STRING scalar, vector, pair or matrix.
    type : Constant
        Specifies the data type of the integer, which can be CHAR, SHORT, INT or LONG.
    radix : Constant, optional
        An integer in [2, 16] that represents the radix (the base in mathematical numeral systems)
        of the integer. The default value is 10.

        - For radix 2, only '0' and '1' are allowed.

        - For radix 11-16, 'A'/'a' to 'F'/'f' (case insensitive) are used for 10-15.

        - Specifically for radix 16, leading '0x' or '0X' is allowed.

    Returns
    -------
    Constant
            A CHAR/SHORT/INT/LONG scalar/vector/pair/matrix of the same shape as X.
    """
    ...


@builtin_function(_parseInteger)
def parseInteger(X: Constant, type: Constant, radix: Constant = DFLT) -> Constant:
    r"""parseInteger parses X into an integer of the specified type in specified radix.
    If it encounters a character that is not a numeral in the specified radix, it
    ignores it and all succeeding characters and returns the integer value parsed
    up to that point. An exception will be thrown if the first character is invalid.

    Parameters
    ----------
    X : Constant
        A STRING scalar, vector, pair or matrix.
    type : Constant
        Specifies the data type of the integer, which can be CHAR, SHORT, INT or LONG.
    radix : Constant, optional
        An integer in [2, 16] that represents the radix (the base in mathematical numeral systems)
        of the integer. The default value is 10.

        - For radix 2, only '0' and '1' are allowed.

        - For radix 11-16, 'A'/'a' to 'F'/'f' (case insensitive) are used for 10-15.

        - Specifically for radix 16, leading '0x' or '0X' is allowed.

    Returns
    -------
    Constant
            A CHAR/SHORT/INT/LONG scalar/vector/pair/matrix of the same shape as X.
    """
    ...


@builtin_function(_parseJsonTable)
def parseJsonTable(json: Constant, schema: Constant = DFLT, keyCaseSensitive: Constant = DFLT) -> Constant:
    r"""Parses JSON objects into an in-memory table. An empty JSON object will
    parsed as an empty row of the table.

    - When json is a string containing multiple JSON objects, each object will
      be converted to a row in the table.

    - When json is a vector of strings, each element will be converted to a row in the table.

    Parameters
    ----------
    json : Constant
        A STRING scalar or vector containing JSON objects. If it is a STRING scalar,
        it can contain one or more JSON objects. JSON arrays and recursive JSON
        objects are not supported yet.
    schema : Constant, optional
        A table that specifies the column names and types. It can contain the following columns:

        +-------+-----------------------------------------------+
        | Column| Description                                   |
        +=======+===============================================+
        | name  | a string representing the column name         |
        +-------+-----------------------------------------------+
        | type  | a string representing the column type.        |
        +-------+-----------------------------------------------+
        | format| a string specifying the format of date or     |
        |       | time columns.                                 |
        +-------+-----------------------------------------------+

    keyCaseSensitive : Constant, optional
        Indicates whether keys are case-sensitive. true (default) means case
        sensitive, false means case insensitive.
    """
    ...


@builtin_function(_partial)
def partial(func: Constant, *args) -> Constant:
    r"""Create a partial application.

    Parameters
    ----------
    func : Constant
        A function.
    """
    ...


@builtin_function(_partition)
def partition(partitionCol: Constant, keys: Constant) -> Constant:
    r"""Select one or more partitions from a partitioned table. It can only be
    used in the where clause of a SQL statement. This function makes it convenient
    to select specific partitions for HASH, LIST and RANGE partitions.

    Parameters
    ----------
    partitionCol : Constant
        A  STRING indicating the partitioning column. For COMPO partitions,
        specify either of the partitioning columns.
    keys : Constant
        A scalar or vector without null values, indicating the partition(s) to
        select. Please refer to the following table about how to specify keys
        for each partition scheme:

        +------------------+-------------------------------------------+
        | Partition Scheme | How to Specify keys                       |
        +==================+===========================================+
        | VALUE            | The associated element(s) in the          |
        |                  | partitioning vector                       |
        +------------------+-------------------------------------------+
        | RANGE            | The index of the associated partition(s), |
        |                  | starting from 0                           |
        +------------------+-------------------------------------------+
        | HASH             | Hash modulus(moduli) of the partitioning  |
        |                  | column                                    |
        +------------------+-------------------------------------------+
        | LIST             | The index of the associated partition(s), |
        |                  | starting from 0                           |
        +------------------+-------------------------------------------+

        .. note::

            The partitions specified by keys must be within the partition range
            of the partitioned table, otherwise an error would occur indicating
            the specified keys are out of range.
    """
    ...


@builtin_function(_pca)
def pca(X: Constant, colNames: Constant = DFLT, k: Constant = DFLT, normalize: Constant = DFLT, maxIter: Constant = DFLT, svdSolver: Constant = DFLT, randomState: Constant = DFLT) -> Constant:
    r"""Conduct principal component analysis for the specified columns of the data source. Return a dictionary with the following keys:

    - components: the matrix of principal component coefficients with size(colNames) rows and k columns.

    - explainedVarianceRatio: a vector of length k with the percentage of the total variance explained by each of the first k principal component.

    - singularValues: a vector of length k with the principal component variances (eigenvalues of the covariance matrix).

    Parameters
    ----------
    X : Constant
        One or multiple data source. It is usually generated by function sqlDS.
    colNames : Constant, optional
        A string vector indicating column names. The default value is the names
        of all columns in ds.
    k : Constant, optional
        A positive integer indicating the number of principal components.
        The default value is the number of columns in ds.
    normalize : Constant, optional
        A Boolean value indicating whether to normalize each column. The default value is false.
    maxIter : Constant, optional
        A positive integer indicating the number of iterations when svdSolver="randomized".
        If it is not specified, maxIter=7 if k<0.1*cols and maxIter=7 otherwise.
        Here cols means the number of columns in ds.
    svdSolver : Constant, optional
        A string. It can take the value of "full", "randomized" or "auto".
        svdSolver="full" is suitable for situations where k is close to size(colNames);
        svdSolver="randomized" is suitable for situations where k is much smaller than
        size(colNames). The default value is "auto", which means the system automatically
        determines whether to use "full" or "randomized".
    randomState : Constant, optional
        An integer indicating the random seed. It only takes effect when set
        svdSolver="randomized". The default value is int(time(now())).
    """
    ...


@builtin_function(_pcall)
def pcall(func: Constant, *args) -> Constant:
    r"""Conduct parallel computing of a vector function. pcall divides each argument
    into multiple parts and conducts the calculation in parallel. If the length of
    the vectors or table columns of the input variables is less than 100,000,
    pcall will not conduct the calculation in parallel.

    Parameters
    ----------
    func : Constant
        An aggregate function. The output of the function must be a vector or a
        table with the same length as all vectors or table columns in args.
    """
    ...


@builtin_function(_pcross)
def pcross(func: Constant, X: Constant, Y: Constant = DFLT) -> Constant:
    r"""pcross is the parallel computing version of template function cross.

    Parameters
    ----------
    func : Constant
        A binary function.
    X : Constant
        Can be pair/vector/matrix.
    Y : Constant, optional
        Can be pair/vector/matrix. Y is optional.
    """
    ...


@builtin_function(_percentChange)
def percentChange(X: Constant, n: Constant = DFLT) -> Constant:
    r"""For each element Xi in X, return (Xi / Xi-n) - 1, representing the percentage
    changes between elements.

    Parameters
    ----------
    X : Constant
        A vector or matrix.
    n : Constant, optional
        An integer specifying the step to shift when comparing elements in X.
        The default value is 1, meaning to compare the current element with the
        adjacent element at left.

    Returns
    -------
    Constant
        A vector or matrix with the same shape as X.
    """
    ...


@builtin_function(_percentile)
def percentile(X: Constant, percent: Constant, interpolation: Constant = DFLT) -> Constant:
    r"""If X is a vector, return the given percentile of X. The calculation ignores null values.

    If X is a matrix, conduct the aforementioned calculation within each column of X.
    The result is a vector

    If X is a table, conduct the aforementioned calculation within each column of X.
    The result is a table.

    Parameters
    ----------
    X : Constant
        A vector, a matrix or a table.
    percent : Constant
        An integer or a floating number between 0 and 100.
    interpolation : Constant, optional
        A string indicating the interpolation method to use if the specified percentile
        is between two elements in X (assuming the :math:`i^{th}` and :math:`(i+1)^{th}` element in the sorted X).
        It can take the following values: 'linear', 'lower', 'higher', 'nearest', 'midpoint'.

        The default value of interpolation is 'linear'.
    """
    ...


@builtin_function(_percentileRank)
def percentileRank(X: Constant, score: Constant, method: Constant = DFLT) -> Constant:
    r"""Calculate the percentile (0-100) of a score in a vector with null values ignored.

    Parameters
    ----------
    X : Constant
        A numeric vector/matrix/table. If it is a matrix, calculate the percentile
        for each column and output a vector. If it is a table, calculate the percentile
        for each column and output a table.
    score : Constant
        A scalar. The function will calculate the rank of the score according to the X.
    method : Constant, optional
        A string indicating the method to calculate the percentline. It can be:

        - "excel" (default): The proportion of the number of elements smaller than score to the number of elements not equal to score. If score is not equal to any element in X, then percentile calculation formula will be as below:

        .. math::

            \begin{align*}
            P(\text{score}) &= P_i + \frac{(\text{score}-X_i)\cdot\left(P_{i+1}-P_i\right)}{X_{i+1}-X_i}
            \end{align*}

        - In the formula, :math:`X^i` is the maximum less than score and :math:`X^{i+1}` is the minimum greater than score. :math:`P^i` and :math:`P^{i+1}` is the percentile of :math:`X^i` and :math:`X^{i+1}`.

        - "rank": The percentage of the number of elements not greater than score to the number of elements in X. If there are multiple elements in X that is equal to score, take the average of their percentiles as the result.

        - "strict": The percentage of the number of elements smaller than score to the number of elements in X.

        - "weak": The percentage of the number of elements not greater than score to the number of elements in X.

        - "mean": The average value of "strict" and "weak".
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_piecewiseLinFit)
    def piecewiseLinFit(X: Constant, Y: Constant, numSegments: Constant, XC: Constant = DFLT, YC: Constant = DFLT, bounds: Constant = DFLT, lapackDriver: Constant = DFLT, degree: Constant = DFLT, weights: Constant = DFLT, method: Constant = DFLT, maxIter: Constant = DFLT, initialGuess: Constant = DFLT, seed: Constant = DFLT) -> Constant:
        r"""Fit a continuous piecewise linear function for a specified number of line segments. Use differential evolution to find the optimal location of breakpoints for a given number of line segments by minimizing the sum of the square error. Note: Due to the randomness of the differential evolution, the results of this function may vary slightly each time.

        The fitted model can be used as an input for function pwlfPredict.

        Parameters
        ----------
        X : Constant
            A numeric vector indicating the data point locations of x. Null value is not allowed.
        Y : Constant
            A numeric vector indicating the data point locations of y. Null value is not allowed.
        numSegments : Constant
            A positive integer indicating the desired number of line segments.
        XC : Constant, optional
            A numeric vector indicating the x locations of the data points that
            the piecewise linear function will be forced to go through. It only
            takes effect when method='de'.
        YC : Constant, optional
            A numeric vector indicating the y locations of the data points that
            the piecewise linear function will be forced to go through.
            It only takes effect when method='de'.
        bounds : Constant, optional
            A numeric matrix of shape (numSegments-1, 2), indicating the bounds
            for each breakpoint location within the optimization.
        lapackDriver : Constant, optional
            A string indicating which LAPACK driver is used to solve the least-squares
            problem. It can be 'gelsd' (default), 'gelsy' and 'gelss'.
        degree : Constant, optional
            A non-negative integer indicating the degree of polynomial to use.
            The default is 1 for linear models. Use 0 for constant models.
        weights : Constant, optional
            A numeric vector indicating the weights used in least-squares algorithms.
            The individual weights are typically the reciprocal of the standard
            deviation for each data point, where weights[i] corresponds to one
            over the standard deviation of the ith data point. Null value is not allowed.
        method : Constant, optional
            A string indicating the model used. It can be:

            - 'nm' (default): Nelder-Mead simplex algorithm.

            - 'bfgs': BFGS algorithm.

            - 'lbfgs': LBFGS algorithm.

            - 'slsqp': Sequential Least Squares Programming algorithm.

            - 'de': Differential Evolution algorithm.
        maxIter : Constant, optional
            An integral scalar or vector indicating the maximum number of iterations
            for the optimization algorithm during the fitting process.
        initialGuess : Constant, optional
            A numeric vector indicating the initial guess for the parameters that
            optimize the function. Its length is numSegments-1.
        seed : Constant, optional
            An integer indicating the random number seed used in the differential
            evolution algorithm to ensure the reproducibility of results. It only
            takes effect when method='de' or initialGuess is null. If not specified,
            a non-deterministic random number generator is used.

        Returns
        -------
        Constant
            A dictionary with the following keys:

            - breaks: A floating-point vector indicating the breakpoint locations.

            - beta: A floating-point vector indicating the beta parameter for the linear fit.

            - xData: A floating-point vector indicating the input data point locations of x.

            - yData: A floating-point vector indicating the input data point locations of y.

            - XC: A floating-point vector indicating the x locations of the data points that the piecewise linear function will be forced to go through.

            - YC: A floating-point vector indicating the y locations of the data points that the piecewise linear function will be forced to go through.

            - weights: A floating-point vector indicating the weights used in least-squares algorithms.

            - degree: A non-negative integer indicating the degree of polynomial.

            - lapackDriver: A string indicating the LAPACK driver used to solve the least-squares problem.

            - numParameters: An integer indicating the number of parameters.

            - predict: The function used for prediction. The method is called by model.predict(X, [beta], [breaks]). See pwlfPredict.

            - modelName: A string "Piecewise Linear Regression" indicating the model name.
        """
        ...


@builtin_function(_pivot)
def pivot(func: Constant, funcArgs: Constant, rowAlignCol: Constant, colAlignCol: Constant) -> Constant:
    r"""Rearrange the results of an aggregate function as a matrix.

    Assume rowAlignCol has n unique elements and colAlignCol has m unique elements.
    The template will return an n (row) by m (column) matrix, with unique values
    of rowAlignCol as row labels and unique values of colAlignCol as column labels.
    For each element of the matrix, the given function is applied conditional on
    rowAlignCol and colAlignCol equal to corresponding values indicated by the
    cell's row and column labels.

    Parameters
    ----------
    func : Constant
        An aggregate function.
    funcArgs : Constant
        The parameters of func. It is a tuple if there are more than 1 parameter of func.
    rowAlignCol : Constant
        The grouping variable for the rows of the result.
    colAlignCol : Constant
        The grouping variable for the columns of the result.
    """
    ...


@builtin_function(_pj)
def pj(leftTable: Constant, rightTable: Constant, matchingCols: Constant, rightMatchingCols: Constant = DFLT) -> Constant:
    r"""Prefix join is similar to equi join with the following differences:

    - Prefix join returns the rows in the left table whose joining column value
      starts with the joining column value in the right table.

    - Prefix join can only have one joining column, and it must be of data type STRING or SYMBOL.

    .. note::

        When both the left and right tables are DFS tables, pj only matches data
        within the corresponding partitions of the DFS tables.

    Parameters
    ----------
    leftTable : Constant
        The table to be joined.
    rightTable : Constant
        The table to be joined.
    matchingCols : Constant
        A string scalar indicating the matching column.
    rightMatchingCols : Constant, optional
        A string scalar indicating the matching column in rightTable. This optional
        argument must be specified if the matching column has different names in
        leftTable and rightTable. The joining column name in the result will be
        the joining column name from the left table.
    """
    ...


@builtin_function(_ploadText)
def ploadText(filename: Constant, delimiter: Constant = DFLT, schema: Constant = DFLT, skipRows: Constant = DFLT, arrayDelimiter: Constant = DFLT, containHeader: Constant = DFLT, arrayMarker: Constant = DFLT) -> Constant:
    r"""Load a text data file in parallel as an in-memory partitioned table. When the file is greater than 16 MB, it returns a in-memory table with sequential partitions. A regular in-memory table is returned otherwise.

    .. note::

        - The partitioned table returned by ploadText distributes data evenly across all partitions. Each partition holds between 8-16 MB of data.

        - ploadText is faster than loadText with concurrent data loading.

    Parameters
    ----------
    filename : Constant
        The input text file name with its absolute path. Currently only .csv files are supported.
    delimiter : Constant, optional
        A STRING scalar indicating the table column separator. It can consist of
        one or more characters, with the default being a comma (',').
    schema : Constant, optional
        A table. It can have the following columns, among which "name" and "type"
        columns are required.

        +-------+-----------+-------------------------------+
        | Column| Data Type | Description                   |
        +=======+===========+===============================+
        | name  | STRING    | column name                   |
        |       | scalar    |                               |
        +-------+-----------+-------------------------------+
        | type  | STRING    | data type                     |
        |       | scalar    |                               |
        +-------+-----------+-------------------------------+
        | format| STRING    | the format of temporal columns|
        |       | scalar    |                               |
        +-------+-----------+-------------------------------+
        | col   | INT       | the columns to be loaded      |
        |       | scalar or |                               |
        |       | vector    |                               |
        +-------+-----------+-------------------------------+

        .. note::

            If "type" specifies a temporal data type, the format of the source
            data must match a DolphinDB temporal data type. If the format of the
            source data and the DolphinDB temporal data types are incompatible,
            you can specify the column type as STRING when loading the data and
            convert it to a DolphinDB temporal data type using the temporalParse
            function afterwards.

    skipRows : Constant, optional
        An integer between 0 and 1024 indicating the rows in the beginning of
        the text file to be ignored. The default value is 0.
    arrayDelimiter : Constant, optional
        A single character indicating the delimiter for columns holding the array
        vectors in the file. You must use the schema parameter to update the data
        type of the type column with the corresponding array vector data type before import.
    containHeader : Constant, optional
        A Boolean value indicating whether the file contains a header row.
        The default value is null.
    arrayMarker : Constant, optional
        A string containing 2 characters or a CHAR pair. These two characters
        represent the identifiers for the left and right boundaries of an array vector.
        The default identifiers are double quotes (").

        - It cannot contain spaces, tabs (\t), or newline characters (\t or \n).

        - It cannot contain digits or letters.

        - If one is a double quote ("), the other must also be a double quote.

        - If the identifier is ', ", or \, a backslash ( \ ) escape character
          should be used as appropriate. For example, arrayMarker="\"\"".

        - If delimiter specifies a single character, arrayMarker cannot contain
          the same character.

        - If delimiter specifies multiple characters, the left boundary of
          arrayMarker cannot be the same as the first character of delimiter.
    """
    ...


@builtin_function(_ploop)
def ploop(func: Constant, *args) -> Constant:
    r"""ploop is the parallel computing version of template function loop .

    Parameters
    ----------
    func : Constant
        A function.
    """
    ...


@builtin_function(_point)
def point(X: Constant, Y: Constant) -> Constant:
    r"""Generate a POINT type data to store the location of a midpoint in the coordinate system.

    The length of a POINT type is 16 bytes. The low 8 bytes are stored in X and
    the high 8 bytes are stored in Y.

    Parameters
    ----------
    X : Constant
        A numeric scalar, pair, vector or matrix. They can be of integral
        (compress or INT128 not included) or floating type.
    Y : Constant
        A numeric scalar, pair, vector or matrix. They can be of integral
        (compress or INT128 not included) or floating type.
    """
    ...


@builtin_function(_poly1d)
def poly1d(model: Constant, X: Constant) -> Constant:
    r"""Calculate the value of the dependent variable for a one-dimensional
    polynomial based on the given coefficients and independent variable.

    Parameters
    ----------
    model : Constant
        A numeric vector indicating the polynomial coefficients in ascending
        powers. It must not contain null values.
    X : Constant
        A numeric scalar or vector indicating the independent variable.
        It must not contain null values.

    Returns
    -------
    Constant
        A numeric vector of the same length as X.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_polyFit)
    def polyFit(X: Constant, Y: Constant, n: Constant, mode: Constant) -> Constant:
        r"""Return a vector indicating the least-squares fit polynomial coefficients
        in ascending powers for a polynomial p(X) of degree n that is a best fit
        (in a least-squares sense) for the data in Y.

        Parameters
        ----------
        X : Constant
            A numeric vector specifying the query points. The points in X
            correspond to the fitted function values contained in Y.
        Y : Constant
            A numeric vector of the same length as X, which specifies the fitted
            values at query points. It must not contain null values.
        n : Constant
            A non-negative scalar indicating the degree of polynomial fit.
        mode : Constant
            A Boolean scalar indicating whether to return a dictionary of a vector.
            Defaults to 0, meaning to return a vector.
        """
        ...


if not sw_is_ce_edition():
    @builtin_function(_polyPredict)
    def polyPredict(model: Constant, X: Constant) -> Constant:
        r"""Calculate the value of the dependent variable for a one-dimensional
        polynomial based on the given coefficients and independent variable.

        Parameters
        ----------
        model : Constant
            A numeric vector indicating the polynomial coefficients in ascending
            powers. It must not contain null values.
        X : Constant
            A numeric scalar or vector indicating the independent variable.
            It must not contain null values.

        Returns
        -------
        Constant
            A numeric vector of the same length as X.
        """
        ...


@builtin_function(_polynomial)
def polynomial(X: Constant, coeffs: Constant) -> Constant:
    r"""Apply the polynomial coefficient vector coeffs on each element of X.
    Return a vector of the same length as X.

    Parameters
    ----------
    X : Constant
        A scalar/vector.
    coeffs : Constant
        A vector indicating the coefficients of a polynomial.
    """
    ...


@builtin_function(_pop_)
def pop_(obj: Constant) -> Constant:
    r"""Remove the last element of X.

    Parameters
    ----------
    obj : Constant
        A vector.
    """
    ...


@builtin_function(_pow)
def pow(X: Constant, Y: Constant) -> Constant:
    r"""Raise all elements of X to the power of Y.

    Please note that the data type of the result is always DOUBLE, even if both X and Y are integers.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix.
    Y : Constant
        A scalar/vector/matrix.
    """
    ...


@builtin_function(_predict)
def predict(model: Constant, X: Constant) -> Constant:
    r"""Make a prediction with the specified prediction model and data. The result
    is a vector with the same number of elements as the the number of rows in X.
    Each element of the vector corresponds to the predicted value of a row in X.

    Parameters
    ----------
    model : Constant
        A dictionary of the specifications of a prediction model. It is generated
        by functions such as randomForestClassifier or randomForestRegressor.
    X : Constant
        A table. The column names must be the same as the column names in the
        table used to train the prediction model.
    """
    ...


@builtin_function(_prev)
def prev(X: Constant) -> Constant:
    r"""Shift the elements of a vector to the right for one position. In comparison,
    next shifts the elements of a vector to the left for one position; move shifts
    the elements of a vector for multiple positions.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    """
    ...


@builtin_function(_prevState)
def prevState(X: Constant) -> Constant:
    r"""Consecutive elements in X with the same value feature the same state, and a null value has no state. The state of each element refers to its value. Return the previous state of the current element. If it is null, return the previous adjacent state.

    If X is a matrix, return the previous state for each column of the matrix.

    Parameters
    ----------
    X : Constant
        A vector or matrix of temporal/Boolean/numeric type.
    """
    ...


@builtin_function(_print)
def print(*args) -> Constant:
    r"""Print out results and variable contents.
    """
    ...


@builtin_function(_prod)
def prod(X: Constant) -> Constant:
    r"""If X is a vector, return the product of all the elements in X.

    If X is a matrix, calculate the product of all the elements in each column of X and return a vector.

    If X is a table, calculate the product of all the elements in each column of X and return a table.

    As with all aggregate functions, null values are not included in the calculation.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_push_)
def push_(obj: Constant, newData: Constant) -> Constant:
    r"""Append newData to obj. The exclamation mark (!) means in-place change in DolphinDB.

    Parameters
    ----------
    obj : Constant
        A local variable, and it must be a vector/tuple/matrix/table/set.
    newData : Constant
        A scalar/vector/tuple/table/set.

        - If obj is a vector, newData is a scalar, vector, or tuple whose elements
          are of the same type as obj. The result is a vector longer than obj.

        - If obj is a tuple, newData is a scalar, vector or tuple:

          - If newData is a vector, it is appended to obj as one tuple element;

          - If newData is a tuple, the appendTupleAsAWhole configuration parameter
            controls whether it is appended to obj as one tuple element (true) or
            each of its elements is appended independently (false).

        - If obj is a matrix, newData is a vector whose length must be a multiple
          of the number of rows of obj. The result is a matrix with the same number
          of rows as obj but with more columns.

        - If obj is a table, newData is a table with the same number of columns
          as obj. The result is a table with the same number and name of columns as obj but with more rows.

        - If newData and obj are of different data forms, append_ will attempt
          to convert newData to the same data form as obj. If it is not possible, return an error message.
    """
    ...


@builtin_function(_pwj)
def pwj(leftTable: Constant, rightTable: Constant, window: Constant, aggs: Constant, matchingCols: Constant, rightMatchingCols: Constant = DFLT) -> Constant:
    r"""Execuate prevailing window join.

    The differences between pwj and wj are:

    - If rightTable doesn't have a matching value for t+w1 (the left boundary of the window),
      wj will treat it as a null element in the window, whereas pwj will include the
      last value before t+w1 in the window.

    - If rightTable has multiple matching values for t+w1, wj will include all of
      them while pwj will only include the last row.

    Parameters
    ----------
    leftTable : Constant
        The table to be joined.
    rightTable : Constant
        The table to be joined. It cannot be a DFS table.
    window : Constant
        A pair of integers indicating the left bound and the right bound (both are inclusive)
        of the window relative to the records in the left table.
    aggs : Constant
        Ametacode or a tuple of metacode indicating one or a list of aggregate
        functions/rightTable columns. For details please refer to Metaprogramming.
        If an aggregate function is specified, its parameters must be numeric columns
        of the right table. If a rightTable column is specified, the results for
        each window will be output in the form of array vectors.
    matchingCols : Constant
        A string scalar/vector indicating matching columns.
    rightMatchingCols : Constant, optional
        A  string scalar/vector indicating all the matching columns in rightTable.
        This optional argument must be specified if at least one of the matching
        columns has different names in leftTable and rightTable. The joining
        column names in the result will be the joining column names from the left table.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_pwlfPredict)
    def pwlfPredict(model: Constant, X: Constant, beta: Constant = DFLT, breaks: Constant = DFLT) -> Constant:
        r"""Evaluate the fitted continuous piecewise linear function at untested points.

        Parameters
        ----------
        model : Constant
            A dictionary returned by piecewiseLinFit.
        X : Constant
            A numeric vector indicating the x locations to predict the output of
            the fitted continuous piecewise linear function. Null value is not allowed.
        beta : Constant, optional
            A numeric vector indicating the model parameters for the continuous
            piecewise linear fit. Null value is not allowed.
        breaks : Constant, optional
            A numeric vector indicating the x locations where each line segment terminates.
            These are referred to as breakpoints for each line segment. Null value is not allowed.

        Returns
        -------
        Constant
            A floating-point vector.
        """
        ...


if not sw_is_ce_edition():
    @builtin_function(_qclp)
    def qclp(r: Constant, V: Constant, k: Constant, A: Constant = DFLT, b: Constant = DFLT, Aeq: Constant = DFLT, beq: Constant = DFLT, x0: Constant = DFLT, c: Constant = DFLT, eps: Constant = DFLT, alpha: Constant = DFLT) -> Constant:
        r"""Solve the following optimization problem with a linear objective
        function and a set of constraints including a quadratic constraint.

        :math:`\min\limits_xr^T * x\text{ such that}\begin{cases}x^T * V * x\le k\\A * x \le b\\Aeq * x=beq\\norm(x-x_0) \le c\end{cases}`

        The result is a 2-element tuple. The first element is the minimum value
        of the objective function. The second element is the value of x where
        the value of the objective function is minimized.

        Parameters
        ----------
        r : Constant
            A matrix.
        k : Constant
            A positive scalar.
        A : Constant, optional
            A matrix.
        b : Constant, optional
            A vector.
        Aeq : Constant, optional
            A vector.
        beq : Constant, optional
            A vector.
        x0 : Constant, optional
            A vector of coefficients for absolute value inequality constraints.
        c : Constant, optional
            A non-negative number representing the right-hand constant for absolute
            value inequality constraints.
        eps : Constant, optional
            A positive floating-point number representing the solution precision.
            The default value is 1e-6, and the range is [1e-4, 1e-9]. A solution
            with higher precision can be obtained by decreasing eps. If a value
            beyond the range is set, it will be adjusted to the default value.
        alpha : Constant, optional
                positive floating-point number representing the relaxation parameter.
                The default value is 1.5, and the range is (0,2). The solution process
                can be sped up by increasing alpha. If a value beyond the range is set,
                it will be adjusted to the default value.
        """
        ...


@builtin_function(_qr)
def qr(obj: Constant, mode: Constant = DFLT, pivoting: Constant = DFLT) -> Constant:
    r"""Perform the QR decomposition of a matrix. Decompose a matrix A into an orthogonal matrix Q and an upper triangular matrix R, with A=Q*R.

    Given an m-by-n matrix A:

    - If mode="full", return 2 matrices: Q (m-by-m) and R (m-by-n).

    - If mode="economic", return 2 matrices: Q (m-by-k) and R (k-by-n) with k=min(m,n).

    - If mode="r", only return matrix R (m-by-n).

    If pivoting= true, also return a vector P which has the same length as the number of columns of the matrix. P is the pivoting for rank-revealing QR decomposition indicating the location of 1s in the permutation matrix.

    Parameters
    ----------
    obj : Constant
        A matrix.
    mode : Constant, optional
        A string indicating what information is to be returned. It can be "full", "economic" or "r". The default value is "full".
    pivoting : Constant, optional
        A Boolean value. The default value is false.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_quadprog)
    def quadprog(H: Constant, f: Constant, A: Constant = DFLT, b: Constant = DFLT, Aeq: Constant = DFLT, beq: Constant = DFLT) -> Constant:
        r"""Solve the following optimization problem with a quadratic objective function and a set of linear constraints.

        :math:`\substack{\displaystyle{\min}\limits_x} \displaystyle{\frac{1}{2}}x^THx + f^T x\text{ such that}\begin{cases}A\cdot x\le b\\Aeq \cdot x=beq\end{cases}`

        The result is a 2-element tuple. The first element is the minimum value of the objective function. The second element is the value of x where the value of the objective function is minimized.

        Parameters
        ----------
        H : Constant
            A matrix.
        f : Constant
            _description_
        A : Constant, optional
            The coefficient matrix of linear inequality constraints.
        b : Constant, optional
            The right-hand-side vector of the linear inequality constraint.
        Aeq : Constant, optional
            A linear equality constraint coefficient matrix.
        beq : Constant, optional
            The right-hand-side vector of the linear equality constraint.
        """
        ...


@builtin_function(_quantile)
def quantile(X: Constant, q: Constant, interpolation: Constant = DFLT) -> Constant:
    r"""Return values at the given quantile in X.

    Parameters
    ----------
    X : Constant
        A numeric vector, matrix or table.
    q : Constant
        A floating number between 0 and 1.
    interpolation : Constant, optional
        A string indicating how to interpolate if the quantile is between element i and j in X with i<j. It can take the following values:

        - 'linear' (default): i+(j-i)*fraction, where fraction is the decimal part of q*size(X).

        - 'lower': i

        - 'higher': j

        - 'nearest': i or j whichever is nearest.

        - 'midpoint': (i+ j)/2
    """
    ...


@builtin_function(_quantileSeries)
def quantileSeries(X: Constant, q: Constant, interpolation: Constant = DFLT) -> Constant:
    r"""Return values at the given quantile in X.

    Parameters
    ----------
    X : Constant
        A numeric vector.
    q : Constant
        A scalar or vector of floating numbers between 0 and 1.
    interpolation : Constant, optional
        A string indicating how to interpolate if the quantile is between element i and j in X with i<j. It can take the following values and the default value is 'linear'.

        - 'linear' (default): i+(j-i)*fraction, where fraction is the decimal part of q*size(X).

        - 'lower': i

        - 'higher': j

        - 'nearest': i or j whichever is nearest.

        - 'midpoint': (i+ j)/2
    """
    ...


@builtin_function(_quarterBegin)
def quarterBegin(X: Constant, startingMonth: Constant = DFLT, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""Return the first day of the quarter that X belongs to. The first months
    of the quarters are determined by startingMonth. Note that startingMonth=1
    is equivalent to startingMonth=4, 7 or 10.

    If parameter offset is specified, the result is updated every n quarters.
    The parameters offset and n must be specified together, and offset takes effect only when n > 1.

    Parameters
    ----------
    X : Constant
        A scalar/vector of data type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    startingMonth : Constant, optional
        An integer between 1 and 12 indicating a month. The default value is 1.
    offset : Constant, optional
        A scalar of the same data type as X. It must be no greater than the minimum
        value of X. The default value is the minimum value of X.
    n : Constant, optional
        A positive integer. The default value is 1.
    """
    ...


@builtin_function(_quarterEnd)
def quarterEnd(X: Constant, endingMonth: Constant = DFLT, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""Return the first day of the quarter that X belongs to. The first months of
    the quarters are determined by startingMonth. Note that startingMonth=1 is
    equivalent to startingMonth=4, 7 or 10.

    If parameter offset is specified, the result is updated every n quarters. The
    parameters offset and n must be specified together, and offset takes effect only when n > 1.

    Parameters
    ----------
    X : Constant
        A scalar/vector of data type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    endingMonth : Constant, optional
        An integer between 1 and 12 indicating a month. The default value is 1.
    offset : Constant, optional
        A scalar of the same data type as X. It must be no greater than the
        minimum value of X. The default value is the minimum value of X.
    n : Constant, optional
        A positive integer. The default value is 1.
    """
    ...


@builtin_function(_rad2deg)
def rad2deg(X: Constant) -> Constant:
    r"""Convert angle units from radians to degrees for each element of X.

    Parameters
    ----------
    X : Constant
        A scalar/vector.
    """
    ...


@builtin_function(_rand)
def rand(X: Constant, count: Constant = DFLT) -> Constant:
    r"""Return a random scalar/vector/matrix of the same data type as X.

    - If X is a scalar, X must be a positive numerical value. Random values are
      generated following a uniform distribution on [0, X).

    - If X is a vector, random values are drawn from the elements of X.

    Parameters
    ----------
    X : Constant
        A scalar/vector.
    count : Constant, optional
        An INT scalar/pair.

        - If count is not specified, a scalar is returned.

        - If count is a scalar, it specifies the length of the output vector.

        - If count is a tuple, it specifies the dimensions of the output matrix.
    """
    ...


@builtin_function(_randBeta)
def randBeta(alpha: Constant, beta: Constant, count: Constant) -> Constant:
    r"""Return a vector of random values with beta distribution.

    Parameters
    ----------
    alpha : Constant
        A positive floating number.
    beta : Constant
        A positive floating number.
    count : Constant
        The number of random values to be generated.
    """
    ...


@builtin_function(_randBinomial)
def randBinomial(trials: Constant, prob: Constant, count: Constant) -> Constant:
    r"""Return a vector of random values with binomial distribution.

    Parameters
    ----------
    trials : Constant
        A positive integer.
    prob : Constant
        A floating number between 0 and 1.
    count : Constant
        The number of random values to be generated.
    """
    ...


@builtin_function(_randChiSquare)
def randChiSquare(df: Constant, count: Constant) -> Constant:
    r"""Return a vector of random values with chi-squared distribution.

    Parameters
    ----------
    df : Constant
        A positive integer indicating the degree of freedom of a chi-squared distribution.
    count : Constant
        The number of random values to be generated.
    """
    ...


@builtin_function(_randDiscrete)
def randDiscrete(v: Constant, p: Constant, count: Constant) -> Constant:
    r"""Generate a sample of size count with random values sampling from v based
    on the specified probability distribution p.

    Parameters
    ----------
    v : Constant
        A vector/tuple indicating the sample data.
    p : Constant
        A vector of floating point type of the same length as v. Each element in
        p must be a positive number, indicating the probability distribution of v.
    count : Constant
        A positive integer indicating the length of the output vector.
    """
    ...


@builtin_function(_randExp)
def randExp(mean: Constant, count: Constant) -> Constant:
    r"""Return a vector of random values with exponential distribution.

    Parameters
    ----------
    mean : Constant
        The mean of an exponential distribution.
    count : Constant
        The number of random values to be generated.
    """
    ...


@builtin_function(_randF)
def randF(numeratorDF: Constant, denominatorDF: Constant, count: Constant) -> Constant:
    r"""Return a vector of random values with F distribution.

    Parameters
    ----------
    numeratorDF, denominatorDF : Constant
        Positive integers indicating degrees of freedom of an F distribution.

    count : Constant
        The number of random values to be generated.
    """
    ...


@builtin_function(_randGamma)
def randGamma(shape: Constant, scale: Constant, count: Constant) -> Constant:
    r"""Return a vector of random values with gamma distribution.

    Parameters
    ----------
    shape : Constant
        A positive floating number.
    scale : Constant
        A positive floating number.
    count : Constant
        The number of random values to be generated.
    """
    ...


@builtin_function(_randLogistic)
def randLogistic(mean: Constant, s: Constant, count: Constant) -> Constant:
    r"""Return a vector of random values with logistic distribution.

    Parameters
    ----------
    mean : Constant
        The mean of a logistic distribution.
    s : Constant
        The scale parameter of a logistic distribution.
    count : Constant
        The number of random values to be generated.
    """
    ...


@builtin_function(_randMultivariateNormal)
def randMultivariateNormal(mean: Constant, covar: Constant, count: Constant, sampleAsRow: Constant = DFLT) -> Constant:
    r"""Return a matrix of random values that follow a multivariate normal distribution.

    Parameters
    ----------
    mean : Constant
        A vector indicating the mean of a normal distribution.
    covar : Constant
        A positive definite matrix indicating the variance-covariance matrix of
        a multivariate normal distribution.
    count : Constant
        A positive number indicating the number of samples to be generated.
    sampleAsRow : Constant, optional
        A Boolean value. The default value is true indicating each row of the result
        is a sample. Otherwise each column of the result is a sample.
    """
    ...


@builtin_function(_randNormal)
def randNormal(mean: Constant, stdev: Constant, count: Constant) -> Constant:
    r"""Return a vector of random values with normal distribution.

    Parameters
    ----------
    mean : Constant
        The mean of a normal distribution.
    stdev : Constant
        The standard deviation of a normal distribution.
    count : Constant
        The number of random values to be generated.
    """
    ...


@builtin_function(_randPoisson)
def randPoisson(mean: Constant, count: Constant) -> Constant:
    r"""Return a vector of random values with Poisson distribution.

    Parameters
    ----------
    mean : Constant
        The mean of a Poisson distribution.
    count : Constant
        The number of random values to be generated.
    """
    ...


@builtin_function(_randStudent)
def randStudent(df: Constant, count: Constant) -> Constant:
    r"""Return a vector of random values with Student's t-distribution.

    Parameters
    ----------
    df : Constant
        A positive floating number indicating the degree of freedom of a Student's t-distribution.
    count : Constant
        The number of random values to be generated.
    """
    ...


@builtin_function(_randUniform)
def randUniform(lower: Constant, upper: Constant, count: Constant) -> Constant:
    r"""Return a vector of random values with continuous uniform distribution.

    Parameters
    ----------
    lower : Constant
        A numeric scalar indicating the lower bound of a continuous uniform distribution.
    upper : Constant
        A numeric scalar indicating the upper bound of a continuous uniform distribution.
    count : Constant
        The number of random values to be generated.
    """
    ...


@builtin_function(_randWeibull)
def randWeibull(alpha: Constant, beta: Constant, count: Constant) -> Constant:
    r"""Return a vector of random values with Weibull distribution.

    Parameters
    ----------
    alpha : Constant
        A positive floating number.
    beta : Constant
        A positive floating number.
    count : Constant
        The number of random values to be generated.
    """
    ...


@builtin_function(_randomForestClassifier)
def randomForestClassifier(ds: Constant, yColName: Constant, xColNames: Constant, numClasses: Constant, maxFeatures: Constant = DFLT, numTrees: Constant = DFLT, numBins: Constant = DFLT, maxDepth: Constant = DFLT, minImpurityDecrease: Constant = DFLT, numJobs: Constant = DFLT, randomSeed: Constant = DFLT) -> Constant:
    r"""Fit a random forest classification model. The result is a dictionary with
    the following keys: numClasses, minImpurityDecrease, maxDepth, numBins, numTress,
    maxFeatures, model, modelName and xColNames. model is a tuple with the result of
    the trained trees; modelName is "Random Forest Classifier".

    The fitted model can be used as an input for function predict .

    Parameters
    ----------
    ds : Constant
        The data sources to be trained. It can be generated with function sqlDS.
    yColName : Constant
        A string indicating the category column.
    xColNames : Constant
        A string scalar/vector indicating the names of the feature columns.
    numClasses : Constant
        A positive integer indicating the number of categories in the category
        column. The value of the category column must be integers in [0, numClasses).
    maxFeatures : Constant, optional
        Aan integer or a floating number indicating the number of features to
        consider when looking for the best split. The default value is 0.

        - if maxFeatures is a positive integer, then consider maxFeatures features at each split.

        - if maxFeatures is 0, then sqrt(the number of feature columns) features are considered at each split.

        - if maxFeatures is a floating number between 0 and 1, then int(maxFeatures * the number of feature columns)
          features are considered at each split.
    numTrees : Constant, optional
        A positive integer indicating the number of trees in the random forest. The default value is 10.
    numBins : Constant, optional
        A positive integer indicating the number of bins used when discretizing continuous features.
        The default value is 32. Increasing numBins allows the algorithm to consider
        more split candidates and make fine-grained split decisions. However, it
        also increases computation and communication time.
    maxDepth : Constant, optional
        A positive integer indicating the maximum depth of a tree. The default value is 32.
    minImpurityDecrease : Constant, optional
        A node will be split if this split induces a decrease of the Gini impurity
        greater than or equal to this value. The default value is 0.
    numJobs : Constant, optional
        An integer indicating the maximum number of concurrently running jobs if
        set to a positive number. If set to -1, all CPU threads are used. If set
        to another negative integer, (the number of all CPU threads + numJobs + 1) threads are used.
    randomSeed : Constant, optional
        The seed used by the random number generator.
    """
    ...


@builtin_function(_randomForestRegressor)
def randomForestRegressor(ds: Constant, yColName: Constant, xColNames: Constant, maxFeatures: Constant = DFLT, numTrees: Constant = DFLT, numBins: Constant = DFLT, maxDepth: Constant = DFLT, minImpurityDecrease: Constant = DFLT, numJobs: Constant = DFLT, randomSeed: Constant = DFLT) -> Constant:
    r"""Fit a random forest regression model. The result is a dictionary with the
    following keys: minImpurityDecrease, maxDepth, numBins, numTress, maxFeatures,
    model, modelName and xColNames. model is a tuple with the result of the trained trees;
    modelName is "Random Forest Regressor".

    The fitted model can be used as an input for function predict .

    Parameters
    ----------
    ds : Constant
        The data sources to be trained. It can be generated with function sqlDS.
    yColName : Constant
        A string indicating the dependent variable column.
    xColNames : Constant
        A string scalar/vector indicating the names of the feature columns.
    maxFeatures : Constant, optional
        An integer or a floating number indicating the number of features to
        consider when looking for the best split. The default value is 0.

        - if maxFeatures is a positive integer, then consider maxFeatures features at each split.

        - if maxFeatures is 0, then sqrt(the number of feature columns) features are considered at each split.

        - if maxFeatures is a floating number between 0 and 1, then int(maxFeatures * the number of feature columns)
          features are considered at each split.
    numTrees : Constant, optional
        A positive integer indicating the number of trees in the random forest. The default value is 10.
    numBins : Constant, optional
            positive integer indicating the number of bins used when discretizing continuous features.
            The default value is 32. Increasing numBins allows the algorithm to consider more split
            candidates and make fine-grained split decisions. However, it also increases computation
            and communication time.
    maxDepth : Constant, optional
        A positive integer indicating the maximum depth of a tree. The default value is 32.
    minImpurityDecrease : Constant, optional
        A node will be split if this split induces a decrease of impurity greater
        than or equal to this value. The default value is 0.
    numJobs : Constant, optional
        An integer indicating the maximum number of concurrently running jobs if
        set to a positive number. If set to -1, all CPU threads are used. If set
        to another negative integer, (the number of all CPU threads + numJobs + 1) threads are used.
    randomSeed : Constant, optional
        The seed used by the random number generator.
    """
    ...


@builtin_function(_rank)
def rank(X: Constant, ascending: Constant = DFLT, groupNum: Constant = DFLT, ignoreNA: Constant = DFLT, tiesMethod: Constant = DFLT, percent: Constant = DFLT, precision: Constant = DFLT) -> Constant:
    r"""Based on the sort order specified by ascending, this function returns the ranking (starting from 0) of each element in X.

    If X is a vector, return a vector with the same length as X:

    - If groupNum is specified, divide the sorted vector X into groupNum groups and return the group number (starting from 0) for each element in X.

      - If the number of elements in X cannot be divided by groupNum, the first mod(size(X), groupNum) groups will hold one more element. For example, X has 6 elements, groupNum is specified as 4, the first and second elements of sorted vector X belong to group 0, the third and fourth elements belong to group 1, and the fifth and sixth elements belong to groups 2 and 3, respectively.

      - If the identical elements are not divided in the same group, return the smallest group number for all identical elements.

    - If ignoreNA = true, null values are ignored and return NULL.

    If X is a matrix/table, conduct the aforementioned calculation within each column of X. The result is a matrix/table with the same shape as X.

    If X is a dictionary, the ranking is based on its values, and the ranks of all elements are returned.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/dictionary.
    ascending : Constant, optional
        A Boolean value indicating whether the sorting is in ascending order.
        The default value is true (ascending).
    groupNum : Constant, optional
        A positive integer indicating the number of groups to sort X into.
    ignoreNA : Constant, optional
        A Boolean value indicating whether null values are ignored.
    tiesMethod : Constant, optional
        A string indicating how to rank the group of elements with the same value (i.e., ties):

        - 'min' : the smallest rank value of the tie values.

        - 'max' : the largest rank value of the tie values.

        - 'average' : the average of the rank values for all ties.

        - 'first': Gives the first found tie value the lowest rank value, and
          continues with the following rank value for the next tie.
    percent : Constant, optional
        A Boolean value, indicating whether to display the returned rankings in
        percentile form. The default value is false.
    precision : Constant, optional
        An integer between [1, 15]. If the absolute difference between two values
        is no greater than 10^(-precision), the two values are considered to be equal.
    """
    ...


@builtin_function(_ratio)
def ratio(X: Constant, Y: Constant) -> Constant:
    r"""Returns element-by-element ratio of X to Y. Function ratio always returns
    floating numbers. If both X and Y are integer/long, ratio converts them into
    floating numbers and then conduct division. This is different from operator
    div (/) , which does not convert integer/long to floating numbers. Another
    difference with div is that Y can be negative integers when X is integer.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix.
    Y : Constant
        A scalar/pair/vector/matrix.
    """
    ...


@builtin_function(_ratios)
def ratios(X: Constant) -> Constant:
    r"""If X is a vector, return X(n)\X(n-1) by scanning X. The first element of the result is always null.

    If X is a matrix, conduct the aforementioned calculation within each column of X. The result is a matrix with the same shape as X.

    Parameters
    ----------
    X : Constant
        A vector or a matrix.
    """
    ...


@builtin_function(_rdp)
def rdp(X: Constant, epsilon: Constant) -> Constant:
    r"""Use RDP (Ramer-Douglas-Peucker) vector compression algorithm to compress the POINT type vector.

    Parameters
    ----------
    X : Constant
        A POINT vector which cannot contain null values.
    epsilon : Constant
        A non-negative DOUBLE type scalar that represents the compression threshold.
    """
    ...


@builtin_function(_reciprocal)
def reciprocal(X: Constant) -> Constant:
    r"""Return element-by-element reciprocal of X. The data type of the result is always DOUBLE.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix.
    """
    ...


@builtin_function(_reduce)
def reduce(func: Constant, X: Constant, init: Constant = DFLT, assembleRule: Union[Alias[Literal["consistent"]], Constant] = DFLT) -> Constant:
    r"""The function of reduce is the same as accumulate. Unlike the template accumulate
    that returns result of each iteration, the template reduce outputs only the
    last result. Refer to accumulate for more information.

    Parameters
    ----------
    func : Constant
        A function.
    X, init : Constant
        - When func is a unary function, X can be a non-negative integer, a unary function, or a null value. init must be specified, which is the parameter of func.

        - When func is a binary function, X can be vector/matrix/table. init is the initial value.

        - When func is a ternary function, X must be a tuple with 2 elements, representing the last two parameters of func.
    assembleRule : Union[Alias[Literal[&quot;consistent&quot;]], Constant], optional
        Indicates how the results of sub-tasks are merged into the final result. It accepts either an integer or a string, with the following options:

        - 0 (or "D"): The default value, which indicates the DolphinDB rule. This means the data type and form of the final result are determined by all sub results. If all sub results have the same data type and form, scalars will be combined into a vector, vectors into a matrix, matrices into a tuple, and dictionaries into a table. Otherwise, all sub results are combined into a tuple.

        - 1 (or "C"): The Consistent rule, which assumes all sub results match the type and form of the first sub result. This means the first sub result determines the data type and form of the final output. The system will attempt to convert any subsequent sub results that don't match the first sub result. If conversion fails, an exception is thrown. This rule should only be used when the sub results' types and forms are known to be consistent. This rule avoids having to cache and check each sub result individually, improving performance.

        - 2 (or "U"): The Tuple rule, which directly combines all sub results into a tuple without checking for consistency in their types or forms.

        - 3 (or "K"): The kdb+ rule. Like the DolphinDB rule, it checks all sub results to determine the final output. However, under the kdb+ rule, if any sub result is a vector, the final output will be a tuple. In contrast, under the DolphinDB rule, if all sub results are vectors of the same length, the final output will be a matrix. In all other cases, the output of the kdb+ rule is the same as the DolphinDB rule.
    """
    ...


@builtin_function(_refCount)
def refCount(obj: Constant) -> Constant:
    r"""Return the number of times a variable is referred to.

    Parameters
    ----------
    obj : Constant
        A string indicating a variable name.
    """
    ...


@builtin_function(_regexCount)
def regexCount(str: Constant, pattern: Constant, offset: Constant = DFLT) -> Constant:
    r"""Search in str from the offset position, and return an integer indicating
    how many times a string that matches pattern occurs in str.

    Parameters
    ----------
    str : Constant
        A string or a string vector.
    pattern : Constant
        An ordinary string scalar or a regular expression pattern to be searched in str.
        Regular expression pattern includes character literals, metacharacters,
        or a combination of both.
    offset : Constant, optional
        A non-negative integer with default value of 0. This optional argument is
        the starting position in str to conduct the count operation. The first
        character in str corresponds to position 0.
    """
    ...


@builtin_function(_regexFind)
def regexFind(str: Constant, pattern: Constant, offset: Constant = DFLT) -> Constant:
    r"""Search in str for another string that matches pattern and return an integer
    that indicates the beginning position of the first matched substring. If no
    substring matches, return -1.

    Parameters
    ----------
    str : Constant
        A string or a string vector.
    pattern : Constant
        An ordinary string scalar or a regular expression pattern to be searched
        in str. Regular expression pattern includes character literals,
        metacharacters, or a combination of both.
    offset : Constant, optional
        A non-negative integer with default value of 0. This optional argument
        is the starting position in str to conduct the search operation. The
        first character in str corresponds to position 0.
    """
    ...


@builtin_function(_regexFindStr)
def regexFindStr(str: Constant, pattern: Constant, onlyFirst: Constant = DFLT, offset: Constant = DFLT) -> Constant:
    r"""Different from regexFind which returns the positions of the matched strings,
    regexFindStr searches from the offset position and returns the matched substring.

    - When str is a scalar:

      - If onlyFirst is set to true, return the first substring that matches pattern. Otherwise return an empty string.

      - If onlyFirst is set to false, return a STRING vector containing all non-overlapping matches. Otherwise return an empty STRING vector.

    - When str is a vector:

      - If onlyFirst is set to true, return the first substring that matches pattern for each string of str. Otherwise return a STRING vector of the same length as str, with all elements being empty strings.

      - If onlyFirst is set to false, return a tuple containing all non-overlapping matches for each string of str. Otherwise return an tuple of the same length as str, with all elements being empty STRING vectors.

    Parameters
    ----------
    str : Constant
        A STRING scalar or vector, indicating the target string to be scanned.
    pattern : Constant
        A string indicating the string pattern with regular expression.
        It can contain literals and metacharacters.
    onlyFirst : Constant, optional
        A Boolean value indicating whether to return only the first substring
        that matches pattern for each string.

        - true (default): Return the first match.

        - false: Return all non-overlapping matches.
    offset : Constant, optional
        A non-negative integer indicating the starting position for the search in str.
        The default value is 0, which is the first position of str.
    """
    ...


@builtin_function(_regexReplace)
def regexReplace(str: Constant, pattern: Constant, replacement: Constant, offset: Constant = DFLT) -> Constant:
    r"""Search in str for another string that matches pattern and and replace every
    occurrence of the matched string or pattern with replacement.

    Parameters
    ----------
    str : Constant
        A string or a string vector.
    pattern : Constant
        An ordinary string scalar or a regular expression pattern to be searched in str.
        Regular expression pattern includes character literals, metacharacters,
        or a combination of both.
    replacement : Constant
        A string scalar. It is used to replace pattern in str.
    offset : Constant, optional
        A non-negative integer with default value of 0. This optional argument is
        the starting position in str to conduct the search and replace operation.
        The first character in str corresponds to positive 0.
    """
    ...


@builtin_function(_regroup)
def regroup(X: Constant, label: Constant, func: Constant, byRow: Constant = DFLT) -> Constant:
    r"""Group the data of a matrix based on user-specified column/row labels and
    apply aggregation on each group.

    regroup is similar to the SQL keyword "group by", except that "group by" is
    applied only on tables whereas this function is applied on matrices.

    .. note::

        It is recommended that the func parameter be specified as a built-in
        aggregate function as built-in functions are optimized internally for optimal performance.

    Parameters
    ----------
    X : Constant
        A matrix.
    label : Constant
        A vector indicating the column/row labels based on which the matrix is
        grouped and aggregated. When byRow = true, the length of label must match
        the number of rows of X. Otherwise, it must match the number of columns of X.
    func : Constant
        A unary aggregate function called on each group of the matrix. It can be
        built-in or user-defined.
    byRow : Constant, optional
        A Boolean. The default value is true, indicating that the matrix will be
        grouped and aggregated by rows. False means to group and aggregate matrix by columns.
    """
    ...


@builtin_function(_remoteRun)
def remoteRun(conn: Constant, script: Constant, *args) -> Constant:
    r"""Send a script or function to a remote database for execution. The
    remoteRun function requires version compatibility when the local server is 3.00 or higher.

    Parameters
    ----------
    conn : Constant
        Represents a database connection.
    script : Constant
        A string indicating the script to be executed on the remote node.
    """
    ...


@builtin_function(_remoteRunCompatible)
def remoteRunCompatible(conn: Constant, script: Constant, *args) -> Constant:
    r"""Send a script or function to a remote database for execution.

    Compared to remoteRun, remoteRunCompatible works across all database versions.
    The remoteRun function requires version compatibility when the local server is 3.00 or higher.

    Parameters
    ----------
    conn : Constant
        Represents a database connection.
    script : Constant
        A string indicating the script or function name to be executed on the remote node.
    """
    ...


@builtin_function(_remoteRunWithCompression)
def remoteRunWithCompression(conn: Constant, script: Constant, *args) -> Constant:
    r"""The function has the same feature and usage as the function remoteRun.
    The only difference lies in that remoteRunWithCompression compresses tables
    with more than 1,024 rows during transmission.

    Parameters
    ----------
    conn : Constant
        The connection handle to a remote database.
    script : Constant
        The script or function to be executed.
    """
    ...


@builtin_function(_removeHead_)
def removeHead_(obj: Constant, n: Constant) -> Constant:
    r"""Delete the first n elements from a vector.

    Parameters
    ----------
    obj : Constant
        A vector.
    n : Constant
        A positive integer indicating the number of elements at the beginning of
        the vector to be removed.
    """
    ...


@builtin_function(_removeTail_)
def removeTail_(obj: Constant, n: Constant) -> Constant:
    r"""Delete the last n elements from a vector.

    Parameters
    ----------
    obj : Constant
        A  vector.
    n : Constant
        A positive integer indicating the number of elements at the end of the vector to be removed.
    """
    ...


@builtin_function(_rename_)
def rename_(a: Constant, b: Constant, c: Constant = DFLT) -> Constant:
    r"""For a vector, assign a new name.

    For a matrix, add or change columns names or row names.

    For a table, rename the columns.

    Parameters
    ----------
    a : Constant
        A vector, regular/indexed matrix, in-memory table, or DFS table (for OLAP engine only).

        - When a is a vector, b is a string/symbol.

        - When a is a matrix, if c is not specified, b is the column lables; if c is specified, b is the row labels and c is the column lables. Column and row labels must match the respective dimensions of a. b and c could be data of any types. Note that for an indexed matrix, b and c must be strictly increasing vectors, otherwise an error will be thrown.

        - When a is an in-memory table, b and c is a string scalar or vector. If c is not specified, b is new column names starting from the first column on the left; if c is specified, b is the old column names and c is the corresponding new column names. Users should make sure the number of new or old column names be less than or equal to the total number of columns in the table.

        - When a is a DFS table, b and c must be a string. If c is not specified, b is new column names starting from the first column on the left; if c is specified, b is the old column names and c is the corresponding new column names. Users should make sure the number of new or old column names be less than or equal to the total number of columns in the table;
    """
    ...


@builtin_function(_renameTable)
def renameTable(dbHandle: Constant, tableName: Constant, newTableName: Constant) -> Constant:
    r"""Rename a table in a DFS database.

    Parameters
    ----------
    dbHandle : Constant
        A DFS database handle.
    tableName : Constant
        A string indicating a table name. The table can be either a DFS table or a dimension table.
    newTableName : Constant
        A string indicating the new table name.
    """
    ...


@builtin_function(_reorderColumns_)
def reorderColumns_(table: Constant, reorderedColNames: Constant) -> Constant:
    r"""Change the order of columns of an in-memory table. It modifies the original
    table instead of creating a new table.

    Parameters
    ----------
    table : Constant
        An in-memory table that is not shared.
    reorderedColNames : Constant
        A string vector indicating column names. It specifies the order of columns
        after execution. We only need to write the names for the columns whose
        positions are changed and all columns before them in the new table. For
        example, if we switch the position of the 3th column and the 6th column,
        then we only need to specify the names of the first 6 columns.
    """
    ...


@builtin_function(_repartitionDS)
def repartitionDS(query: Constant, column: Constant = DFLT, partitionType: Constant = DFLT, partitionScheme: Constant = DFLT, local: Constant = DFLT) -> Constant:
    r"""Repartition a table with specified partitioning type and scheme, and return
    a tuple of data sources.

    If query is metacode of SQL statements, the parameter column must be specified.
    For a partitioned table with a COMPO domain, partitionType and partitionScheme
    can be unspecified. In this case, the data sources will be determined based on
    the original partitionType and partitionScheme of column.

    If query is a tuple of metacode of SQL statements, the following 3 parameters
    should be unspecified. The function returns a tuple with the same length as query.
    Each element of the result is a data source corresponding to a piece of metacode in query.

    Parameters
    ----------
    query : Constant
        A metacode of SQL statements or a tuple of metacode of SQL statements.
    column : Constant, optional
        A string indicating a column name in query. Function repartitionDS
        deliminates data sources based on column.
    partitionType : Constant, optional
        Means the type of partition. It can take the value of VALUE or RANGE.
    partitionScheme : Constant, optional
        A vector indicating the partitioning scheme. For details please refer to
        DistributedComputing.
    local : Constant, optional
        A Boolean value indicating whether to fetch the data sources to the local
        node for computing. The default value is true. When set to false, if
        repartitionDS is called on a compute node within a compute group, data
        sources are fetched to all compute nodes within the group; Otherwise data
        sources are fetched to all data nodes and compute nodes which are not
        included in any compute groups.
    """
    ...


@builtin_function(_repeat)
def repeat(X: Constant, n: Constant) -> Constant:
    r"""Repeats each item in string X n times to form a new string. The size of
    the result is the same as the size of X.

    Parameters
    ----------
    X : Constant
        A string scalar/vector.
    n : Constant
        A positive integer.
    """
    ...


@builtin_function(_replace)
def replace(X: Constant, oldValue: Constant, newValue: Constant) -> Constant:
    r"""Replace oldValue with newValue in X. replace_ is the in-place change version of replace.

    Parameters
    ----------
    obj : Constant
        A vector/matrix.
    oldValue : Constant
        A scalar indicating the value to be replaced.
    newValue : Constant
        A scalar of the same category as X, indicating the new value.


    ====================
    [replace_]
    ====================
    """
    ...


@builtin_function(_replace_)
def replace_(obj: Constant, oldValue: Constant, newValue: Constant) -> Constant:
    ...


@builtin_function(_replaceColumn_)
def replaceColumn_(table: Constant, colName: Constant, newCol: Constant) -> Constant:
    r"""- When table is an in-memory table:

      - replaceColumn_ replaces table column(s) with the specified vector(s).
        The data type of the new column is the same as the data type of the specified vector.
        It supports replacing multiple columns at once. Note that the multi-column
        replacement operation is not atomic, which means in cases of system errors,
        some specified column replacements may succeed while others fail partway through.

      - To update column's value without changing its data type, we can use
        both replaceColumn_ and SQL statement update. Only replaceColumn_, however,
        can change a column's data type.

      - When table is a DFS table in the OLAP engine, replaceColumn_ only
        modifies the data type of the specified column(s). Note that:

        - The SYMBOL type cannot be converted to or from other types.

        - Except for SYMBOL, data types within the same category can be converted between each other.

        - INTEGRAL and FLOATING types can be converted between each other.

        - INTEGRAL, FLOATING, LITERAL, and TEMPORAL types can be converted to the STRING type.

    .. note::

        Replacing columns of DECIMAL type is not currently supported.

    Parameters
    ----------
    table : Constant
        A non-shared in-memory table or a DFS table.
    colName : Constant
        A  string indicating the name of the column to replace. When table is an
        in-memory table, colName can also be a vector of strings indicating multiple column names.
    newCol : Constant
        The column values to replace with.

        - When table is an in-memory table:

          - If colName is a scalar, newCol is a vector with the same number of elements as the rows of table.

          - If colName is a vector, newCol is a tuple containing the same number of elements as colName. Each tuple element is a vector with the same number of elements as the rows of table.

        - When table is a DFS table in the OLAP engine, newCol is only used to specify the target data type.
    """
    ...


@builtin_function(_replay)
def replay(inputTables: Constant, outputTables: Constant, dateColumn: Constant = DFLT, timeColumn: Constant = DFLT, replayRate: Constant = DFLT, absoluteRate: Constant = DFLT, parallelLevel: Constant = DFLT, sortColumns: Constant = DFLT, preciseRate: Constant = DFLT) -> Constant:
    r"""Replay one or more tables or data sources (generated by replayDS) to table(s)
    in chronological order to simulate real-time ingestion of streaming data. It is
    commonly used for backtesting of high-frequency trading strategies.

    Parameters
    ----------
    inputTables : Constant
        Can be:

        - for 1-to-1 replay, a non-partitioned in-memory table or data source;

        - for N-to-N/N-to-1 homogeneous replay, multiple non-partitioned in-memory
          tables or a tuple of data sources;

        - for N-to-1 heterogeneous replay, a dictionary. The key of the dictionary
          can be of any data type indicating the unique identifier of the input table,
          and the value is the table object or data source.
    outputTables : Constant
        - for 1-to-1/N-to-1 homogeneous replay, a table object (a non-partitioned
          in-memory table/stream table) or a string scalar with the same schema of the input table.

        - for N-to-N replay, a string vector or tuple of table objects (non-partitioned
          in-memory tables/stream tables) with the same length as that of inputTables.
          The outputTables and inputTables are mapped one-to-one, and each pair has the same schema.

        - for N-to-1 heterogeneous replay, a table object (a non-partitioned in-memory
          table/stream table) containing at least three columns:

          - The first column is of TIMESTAMP type indicating the timestamp
            specified by dateColumn/timeColumn;

          - The second column is of SYMBOL or STRING type indicating the key of
            the dictionary specified in the inputTables;

          - The third column must be of BLOB type that stores the serialized
            result of each replayed record.

          - In addition, you can output the columns with the same column names
            and data types in the input tables.
    dateColumn : Constant, optional
        The column name of the time column. At least one of them must be specified.

        - for 1-to-1/N-to-1 homogeneous replay: it is a string scalar, and the time
          columns in the inputTables and outputTables must use the same name.

        - for N-to-N replay: It is a string scalar if time columns of the input
          tables have same column names; otherwise, it is a string vector.

        - for N-to-1 replay: It is a string scalar if time columns of the input
          tables have same column names; otherwise, it is a dictionary. The key of
          the dictionary is a user-defined string indicating the unique identifier
          of the input table, and the value is dateColumn/timeColumn.

    timeColumn : Constant, optional
        The column name of the time column. At least one of them must be specified.

        - for 1-to-1/N-to-1 homogeneous replay: it is a string scalar, and the time
          columns in the inputTables and outputTables must use the same name.

        - for N-to-N replay: It is a string scalar if time columns of the input
          tables have same column names; otherwise, it is a string vector.

        - for N-to-1 replay: It is a string scalar if time columns of the input
          tables have same column names; otherwise, it is a dictionary. The key of
          the dictionary is a user-defined string indicating the unique identifier
          of the input table, and the value is dateColumn/timeColumn.

        If dateColumn and timeColum are specified as the same column or only one
        of them is specified, there is no restriction on the type of the specified time column.

        If dateColumn and timeColum are specified as different columns, dateColumn
        must be DATE and timeColum can only be SECOND, TIME or NANOTIME.
    replayRate : Constant, optional
        An integer. Together with the parameter absoluteRate, it determines the
        speed of replaying data.
    absoluteRate : Constant, optional
        A Boolean value. The default value is true, indicating that the system
        replays replayRate records per second. If set to false, data is replayed
        at replayRate times the time span of the data.
    parallelLevel : Constant, optional
        A positive integer indicating the number of threads to load data sources
        to memory concurrently. The default value is 1. If inputTables is not a
        data source, there is no need to specify.
    sortColumns : Constant, optional
        A STRING scalar or vector of length 2. Data with the same timestamp is
        sorted according to the specified sortColumns. It is supported only for
        heterogeneous replay.

        Note that any column in either of the input tables can be specified as a
        sort column. If one of the input tables doesn't contain the specified sort
        column, it is filled with null values and treated as the minimum values when the data is sorted.
    preciseRate : Constant, optional
        A Boolean value. The default value is false. If it is set to true, the data
        is replayed at replayRate times the time difference between two adjacent records.
        Note that deviation of a few milliseconds may exist.
    """
    ...


@builtin_function(_replayDS)
def replayDS(sqlObj: Constant, dateColumn: Constant = DFLT, timeColumn: Constant = DFLT, timeRepartitionSchema: Constant = DFLT) -> Constant:
    r"""Generates a tuple of data sources from a DFS table (queried by a SQL statement)
    based on its time columns. It can be further divided by the parameters
    timeColumn and timeRepartitionSchema.

    It is used as the inputs of function replay. To replay a DFS table, the replay
    function must be conjuncted with the replayDS function.

    Parameters
    ----------
    sqlObj : Constant
        Ametacode with SQL statements. The table object in the SQL statement is
        a DFS table and must use a DATE type column as one of the partitioning columns.
    dateColumn : Constant, optional
        Must be a time column of the table queried by the SQL statement, based on
        which the data is sorted. It can be of DATE (most commonly used), MONTH
        or other temporal types. If dateColumn is specified, it must be one of
        the partitioning columns of the DFS table. Data sources are generated
        based on the time precision of the dateColumn, e.g., if the dateColumn
        is partitioned by day, the data source is also divided by day.
    timeColumn : Constant, optional
        Must be a time column of the table queried by the SQL statement, based on
        which the data is sorted. If dateColumn is of DATE type, you can further
        deliminate data sources by specifying timeColumn as SECOND, TIME or NANOTIME type.

        .. note::

            - Currently, parameters dateColumn and timeColumn do not support DATEHOUR type.

            - If dateColumn is not specified, the first column of the table object is
              treated as the date column.

    timeRepartitionSchema : Constant, optional
        A vector of temporal type. If timeColumn is specified, timeRepartitionSchema
        deliminates multiple data sources based on timeColumn. For example, if
        timeRepartitionSchema =[t1, t2, t3], then there are 4 data sources within
        each day: [00:00:00.000,t1), [t1,t2), [t2,t3), and [t3,23:59:59.999).
    """
    ...


@builtin_function(_repmat)
def repmat(X: Constant, rowRep: Constant, colRep: Constant) -> Constant:
    r"""Create a large matrix consisting of a rowRep-by-colRep tiling of copies of X.

    Parameters
    ----------
    X : Constant
        A matrix.
    rowRep : Constant
        An positive integer.
    colRep : Constant
        An positive integer.
    """
    ...


@builtin_function(_resample)
def resample(X: Constant, rule: Constant, func: Constant, closed: Constant = DFLT, label: Constant = DFLT, origin: Constant = DFLT) -> Constant:
    r"""Apply func to X based on the frenquency (or the trading calendar) as specified
    in rule. Note that when rule is specified as the identifier of the trading calendar,
    data generated on a non-trading day will be calculated in the previous trading day.

    Parameters
    ----------
    X : Constant
        A matrix or series with row labels. The row labels must be non-null values
        of temporal type, and must be increasing.
    rule : Constant
        A string that can take the following values:

        +----------------------+-------------------------+
        | Values of parameter  | Corresponding DolphinDB |
        | "rule"               | function                |
        +======================+=========================+
        | "B"                  | businessDay             |
        +----------------------+-------------------------+
        | "W"                  | weekEnd                 |
        +----------------------+-------------------------+
        | "WOM"                | weekOfMonth             |
        +----------------------+-------------------------+
        | "LWOM"               | lastWeekOfMonth         |
        +----------------------+-------------------------+
        | "M"                  | monthEnd                |
        +----------------------+-------------------------+
        | "MS"                 | monthBegin              |
        +----------------------+-------------------------+
        | "BM"                 | businessMonthEnd        |
        +----------------------+-------------------------+
        | "BMS"                | businessMonthBegin      |
        +----------------------+-------------------------+
        | "SM"                 | semiMonthEnd            |
        +----------------------+-------------------------+
        | "SMS"                | semiMonthBegin          |
        +----------------------+-------------------------+
        | "Q"                  | quarterEnd              |
        +----------------------+-------------------------+
        | "QS"                 | quarterBegin            |
        +----------------------+-------------------------+
        | "BQ"                 | businessQuarterEnd      |
        +----------------------+-------------------------+
        | "BQS"                | businessQuarterBegin    |
        +----------------------+-------------------------+
        | "REQ"                | FY5253Quarter           |
        +----------------------+-------------------------+
        | "A"                  | yearEnd                 |
        +----------------------+-------------------------+
        | "AS"                 | yearBegin               |
        +----------------------+-------------------------+
        | "BA"                 | businessYearEnd         |
        +----------------------+-------------------------+
        | "BAS"                | businessYearBegin       |
        +----------------------+-------------------------+
        | "RE"                 | FY5253                  |
        +----------------------+-------------------------+
        | "D"                  | date                    |
        +----------------------+-------------------------+
        | "H"                  | hourOfDay               |
        +----------------------+-------------------------+
        | "min"                | minuteOfHour            |
        +----------------------+-------------------------+
        | "S"                  | secondOfMinute          |
        +----------------------+-------------------------+
        | "L"                  | millisecond             |
        +----------------------+-------------------------+
        | "U"                  | microsecond             |
        +----------------------+-------------------------+
        | "N"                  | nanosecond              |
        +----------------------+-------------------------+
        | "SA"                 | semiannualEnd           |
        +----------------------+-------------------------+
        | "SAS"                | semiannualBegin         |
        +----------------------+-------------------------+

        The strings above can also be used with positive integers for parameter
        rule. For example, "2M" means the end of every two months. In addition,
        rule can also be set as the identifier of the trading calendar, e.g.,
        the Market Identifier Code of an exchange, or a user-defined calendar name.
        Positive integers can also be used with identifiers. For example,
        "2XNYS" means every two trading days of New York Stock Exchange.
    func : Constant
        An aggregate function.
    closed : Constant, optional
        A string indicating which boundary of the interval is closed.

        - The default value is 'left' for all values of rule except for
          'M', 'A', 'Q', 'BM', 'BA', 'BQ', and 'W' which all have a default of 'right'.

        - The default is 'right' if origin is 'end' or 'end_day'.
    label : Constant, optional
        A string indicating which boundary is used to label the interval.

        - The default value is 'left' for all values of rule except for
          'M', 'A', 'Q', 'BM', 'BA', 'BQ', and 'W' which all have a default of 'right'.

        - The default is 'right' if origin is 'end' or 'end_day'.
    origin : Constant, optional
        A string or a scalar of the same data type as X, indicating the timestamp
        where the intervals start. It can be 'epoch', start', 'start_day', 'end',
        'end_day' or a user-defined time object. The default value is 'start_day'.

        - 'epoch': origin is 1970-01-01

        - 'start': origin is the first value of the timeseries

        - 'start_day': origin is 00:00 of the first day of the timeseries

        - 'end': origin is the last value of the timeseries

        - 'end_day': origin is 24:00 of the last day of the timeseries
    """
    ...


@builtin_function(_reshape)
def reshape(obj: Constant, dim: Constant = DFLT) -> Constant:
    r"""Change the dimensions of a matrix and return a new matrix. If dim is not
    specified, reshape obj to a vector.

    Parameters
    ----------
    obj : Constant
        A vector/matrix.
    dim : Constant, optional
        A pair of integers indicating (row dimension):(column dimension) of the result.
    """
    ...


@builtin_function(_residual)
def residual(Y: Constant, X: Constant, params: Constant, intercept: Constant = DFLT) -> Constant:
    r"""Return the residuals from the least squares regression of Y on X.

    .. note::

        - For an in-memory table, the residuals can be obtained setting mode=2 in function ols or wls;

        - For a DFS table, the residuals can only be obtained with function residual.

    Parameters
    ----------
    Y : Constant
        The dependent variable. It is a vector.
    X : Constant
        The independent variable(s). X can be a matrix, table or tuple. When X
        is a matrix, if the number of rows is the same as the length of Y, each
        column of X is a factor; If the number of columns equals the length of Y,
        each row of X is a factor.
    params : Constant
        The regression estimator.
    intercept : Constant, optional
        T Boolean variable indicating whether to include an intercept in the regression.
        The default value is true, meaning that the system automatically adds a
        column of "1" to X to generate the intercept.
    """
    ...


@builtin_function(_restore)
def restore(backupDir: Constant, dbPath: Constant, tableName: Constant, partition: Constant, force: Constant = DFLT, outputTable: Constant = DFLT, parallel: Constant = DFLT, snapshot: Constant = DFLT, keyPath: Constant = DFLT) -> Constant:
    r"""Restore the specified partitions from the most recent backup. Return a
    string vector indicating the path of restored partitions. The function must
    be executed by a logged-in user.

    .. note::

        - To restore the partitions backed up with SQL statements, the parameter
          snapshot should not be true. Otherwise an error is raised.

        - When restoring the partitions backed up with SQL statements, the backup
          data is directly appended to the target restore table; When restoring the
          partitions backed up by copying files, the system only overwrites the
          partitions that have different data.

        - Make sure that the storage engine of the backup database is the same as
          the engine of newDBPath, and the partitionScheme must be the same (except for VALUE).
          For a VALUE partitioned database, the partitioning scheme of the backup database
          must be a subset of that of the database to be restored. For example, if the
          partitioning scheme of the backup database is database("dfs://xxx", VALUE, 2017.08.07..2017.08.11),
          then the partitioning scheme of the target database must be VALUE-based and
          its range must be beyond 2017.08.07..2017.08.11.

    Parameters
    ----------
    backupDir : Constant
        A string indicating the directory where the backup is kept.
    dbPath : Constant
        A string indicating the path of a DFS database.
    tableName : Constant
        A string indicating a DFS table name.
    partition : Constant
        A string indicating the relative path of the partitions to be restored.
        Use "?" as a single wildcard and "%" as a wildcard that can match zero or more characters.

        - To restore all partitions, use "%".

        - To restore a certain partition, specify the relative path or "%" +"partition name".
          For example, to restore the "20170810/50_100" partition
          under "dfs://compoDB", specify "/compoDB/20170807/0_50" or "%/20170807/0_50" as partition path.

        - For versions between 1.30.16/2.00.4 - 1.30.18/2.00.6, if chunkGranularity
          is set to "TABLE" when creating the database, partition must include the
          physical index (which you can get with the listTables function) of the
          selected partition. For example, if the physical index of the
          "/compoDB/20170807/0_50" partition is 8t, then specify partition
          as "/compoDB/20170807/0_50/8t" to restore it.
    force : Constant, optional
        A Boolean value. The default value is false, meaning to perform an incremental
        recovery, i.e., only the partitions with different metadata from that of
        the most recent backup are restored. True means to perform a full recovery.
    outputTable : Constant, optional
        The handle to a DFS table which has the same schema as the backup table.
        If it is unspecified, partitions will be restored to the target table
        specified by tableName; Otherwise, partitions will be restored to outputTable
        whereas the table specified by tableName remains unchanged.
    parallel : Constant, optional
        A Boolean value indicating whether to restore partitions of a table in parallel.
        The default value is false.
    snapshot : Constant, optional
        A Boolean value indicating whether to synchronize the deletion of table/partitions
        in the backup to the restored database. It only takes effect when partition is
        set to "%". If set to true, the deleted tables/partitions in the backup are
        deleted in the target restore database synchronously. Note: For versions
        prior to 2.00.13/3.00.1, the default value for snapshot is true. Since
        version 2.00.13/3.00.1, the default value is false.
    keyPath : Constant, optional
        A STRING scalar that specifies the path to the key file used for restoring
        an encrypted backup. The key version used for restoring the data must
        match the version specified during the backup. Note that when restoring
        an encrypted table, both the backup table and the target table must use
        the same encryption mode (i.e., the same encryptMode parameter specified
        during table creation).
    """
    ...


@builtin_function(_restoreDB)
def restoreDB(backupDir: Constant, dbPath: Constant, newDBPath: Constant = DFLT, keyPath: Constant = DFLT) -> Constant:
    r"""Restore the backup database. Return a table where each row is the restored
    database and table name.

    Similar to function migrate, the function can restore a database, and the
    difference lies in:

    - migrate can restore all databases and tables under a directory, while
      restoreDB can only restore a database.

    - If the names of restored database and tables are the same as the originals,
      the original databases and tables must be deleted before calling migrate,
      which is not required by function restoreDB.

    .. note::

        - This function can only restore a database backed up by copying files
          (when dbPath is specified for function backup).

        - Make sure that the storage engine of the backed-up database is the
          same as the engine of newDBPath, and the partitionScheme (except for VALUE)
          must be the same. For a VALUE partitioned database, the partitioning scheme
          of the backup database must be a subset of that of the database to be restored.

    Parameters
    ----------
    backupDir : Constant
        A string indicating the directory to save the backup.
    dbPath : Constant
        A string indicating the database path.
    newDBPath : Constant, optional
        A string indicating the new database name. The default value is dbPath.
    keyPath : Constant, optional
        A STRING scalar that specifies the path to the key file used for restoring
        an encrypted backup. The key version used for restoring the data must match
        the version specified during the backup. Note that when restoring an
        encrypted table, both the backup table and the target table must use the
        same encryption mode (i.e., the same encryptMode parameter specified during table creation).
    """
    ...


@builtin_function(_restoreTable)
def restoreTable(backupDir: Constant, dbPath: Constant, tableName: Constant, newDBPath: Constant = DFLT, newTableName: Constant = DFLT, keyPath: Constant = DFLT) -> Constant:
    r"""Restore the backup database. Return a table where each row is the restored
    database and table name. The function is equivalent to
    restore(backupDir, dbPath, tableName, force=false, parallel=true, snapshot=true).

    Similar to function migrate, the function can restore all tables of a database,
    and the difference lies in:

    - migrate can restore all databases and tables under a directory, while
      restoreTable can only restore a table.

    - When the names of restored database and tables are the same as the originals,
      the original database and tables must be deleted before calling migrate, which is not required by function restoreTable.

    .. note::

        - This function can only restore a database backed up by copying files
          (when dbPath is specified for function backup).

        - Make sure that the storage engine of the backed-up database is the same
          as the engine of newDBPath, and the partitionScheme (except for VALUE)
          must be the same. For a VALUE partitioned database, the partitioning scheme
          of the backup database must be a subset of that of the database to be restored.

    Parameters
    ----------
    backupDir : Constant
        A string indicating the directory to save the backup.
    dbPath : Constant
        A string indicating the database path.
    tableName : Constant
        A string indicating the table name.
    newDBPath : Constant, optional
        A string indicating the new database name. The default value is dbPath.
    newTableName : Constant, optional
        A string indicating the new table name. The default value is tableName.
    keyPath : Constant, optional
        A STRING scalar that specifies the path to the key file used for restoring
        an encrypted backup. The key version used for restoring the data must match
        the version specified during the backup. Note that when restoring an encrypted
        table, both the backup table and the target table must use the same encryption
        mode (i.e., the same encryptMode parameter specified during table creation).
    """
    ...


@builtin_function(_reverse)
def reverse(X: Constant) -> Constant:
    r"""- If X is a vector or matrix, return a new vector or matrix with reverse order of the original vector or matrix.

    - If X is an ​​in-memory table​, return an in-memory table with reverse ​​row order.

    - If X is an ​​ordered dictionary, return an ordered dictionary where the​​key-value pairs are in reverse order.

    Parameters
    ----------
    X : Constant
        A vector/matrix/in-memory table/ordered dictionary.
    """
    ...


@builtin_function(_ridge)
def ridge(ds: Constant, yColName: Constant, xColNames: Constant, alpha: Constant = DFLT, intercept: Constant = DFLT, normalize: Constant = DFLT, maxIter: Constant = DFLT, tolerance: Constant = DFLT, solver: Constant = DFLT, swColName: Constant = DFLT) -> Constant:
    r"""Linear least squares with l2 regularization.

    Minimize the following objective function:

    .. math::

        \begin{align*}
        &\|y - X w\|_2^2 + \alpha \,\|w\|_2^2
        \end{align*}

    Parameters
    ----------
    ds : Constant
        Aan in-memory table, or a data source, or a list of data sources.
    yColName : Constant
        A string indicating the column name of the dependent variable in ds.
    xColNames : Constant
        A string scalar/vector indicating the column names of the independent variables in ds.
    alpha : Constant, optional
        A floating number representing the constant that multiplies the L1-norm.
        The default value is 1.0.
    intercept : Constant, optional
        A Boolean value indicating whether to include the intercept in the regression.
        The default value is true.
    normalize : Constant, optional
        ABoolean value. If true, the regressors will be normalized before regression
        by subtracting the mean and dividing by the L2-norm. If intercept=false,
        this parameter will be ignored. The default value is false.
    maxIter : Constant, optional
        A positive integer indicating the maximum number of iterations.
        The default value is 1000.
    tolerance : Constant, optional
        A floating number. The iterations stop when the improvement in the objective
        function value is smaller than tolerance. The default value is 0.0001.
    solver : Constant, optional
        A string indicating the solver to use in the computation. It can be either
        'svd' or 'cholesky'. It ds is a list of data sources, solver must be 'cholesky'.
    swColName : Constant, optional
        A STRING indicating a column name of ds. The specified column is used as
        the sample weight. If it is not specified, the sample weight is treated as 1.
    """
    ...


@builtin_function(_ridgeBasic)
def ridgeBasic(Y: Constant, X: Constant, mode: Constant = DFLT, alpha: Constant = DFLT, intercept: Constant = DFLT, normalize: Constant = DFLT, maxIter: Constant = DFLT, tolerance: Constant = DFLT, solver: Constant = DFLT, swColName: Constant = DFLT) -> Constant:
    r"""Perform Ridge regression.

    Minimize the following objective function:

    .. math::

        \begin{align*}
        \lVert y - X w \rVert_2^2 + \alpha \, \lVert w \rVert_2^2
        \end{align*}

    Parameters
    ----------
    Y : Constant
        A numeric vector indicating the dependent variable.
    X : Constant
        Aa numeric vector/tuple/matrix/table indicating the independent variable.

        - When X is a vector/tuple, it must be of the same length as Y.

        - When X is a matrix/table, the number of rows must be the same as the length of Y.

    mode : Constant, optional
        An integer indicating the contents in the output. It can be:

        - 0 (default): a vector of the coefficient estimates.

        - 1: a table with coefficient estimates, standard error, t-statistics, and p-values.

        - 2: a dictionary with the following keys: ANOVA, RegressionStat, Coefficient, and Residual.
    alpha : Constant, optional
        A floating number representing the constant that multiplies the L1-norm.
        The default value is 1.0.
    intercept : Constant, optional
        A Boolean value indicating whether to include the intercept in the regression.
        The default value is true.
    normalize : Constant, optional
        A Boolean value. If true, the regressors will be normalized before regression
        by subtracting the mean and dividing by the L2-norm. If intercept=false,
        this parameter will be ignored. The default value is false.
    maxIter : Constant, optional
        A positive integer indicating the maximum number of iterations. The default value is 1000.
    tolerance : Constant, optional
        A floating number. The iterations stop when the improvement in the objective
        function value is smaller than tolerance. The default value is 0.0001.
    solver : Constant, optional
        A string indicating the solver to use in the computation. It can be either
        'svd' or 'cholesky'. It ds is a list of data sources, solver must be 'cholesky'.
    swColName : Constant, optional
        A STRING indicating a column name of ds. The specified column is used as
        the sample weight. If it is not specified, the sample weight is treated as 1.
    """
    ...


@builtin_function(_right)
def right(X: Constant, n: Constant) -> Constant:
    r"""Return the last n characters of string X.

    Parameters
    ----------
    X : Constant
        A string scalar or vector.
    n : Constant
        A positive integer.
    """
    ...


@builtin_function(_rolling)
def rolling(func: Constant, funcArgs: Constant, window: Constant, step: Constant = DFLT, fill: Constant = DFLT, explicitOffset: Constant = DFLT) -> Constant:
    r"""The rolling function applies func to a moving window of funcArgs. It starts
    calculating when the window size is reached for the first time, then calculates
    with frequency specified by step.

    Similar to the moving function, windows in rolling function are always along rows.

    The differences of rolling and moving functions lie in:

    - The func parameter in rolling function supports aggregate or vectorized functions,
      whereas func in moving function only supports aggregate functions.

    - When func is specified as an aggregate function,

      - step can be specified in rolling function.

      - rolling does not return null values of the first (window -1) elements.

    Parameters
    ----------
    func : Constant
        An aggregate or vectorized function.
    funcArgs : Constant
        The arguments passed to func, which can be vectors, matrices, or tables.
        It is a tuple if there are more than 1 parameter of func, and all arguments
        must have the same size (the number of elements of a vector or rows of a matrix).
    window : Constant
        The window size.
    step : Constant, optional
        The count or interval that windows slide. The default value is 1.
        If func is a vectorized function, step must be equal to window.
    """
    ...


@builtin_function(_rollingPanel)
def rollingPanel(X: Constant, window: Constant, groupingCol: Constant = DFLT) -> Constant:
    r"""Extract a fixed number of rows from a table with a rolling window to generate
    a new table. The rolling window moves by 1 row each time until it reaches the bottom of the table.

    If groupingCol is specified, perform the aforementioned operation in each group.

    The panelNumber column in the result means the index of each extraction operation,
    which starts from 0.

    Parameters
    ----------
    X : Constant
        A table.
    window : Constant
        A positive integer indicating the length of the moving windows.
    groupingCol : Constant, optional
        A string scalar/vector indicating one or some columns in table X.
    """
    ...


@builtin_function(_round)
def round(X: Constant, precision: Constant = DFLT) -> Constant:
    r"""Round a number to the specified number of digits after the decimal point
    with the round half up rule.

    In comparison, functions floor and ceil map a number to the largest previous
    or the smallest following integer, respectively.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix.
    precision : Constant, optional
        An integer indicating the number of digits (up to 10) after the decimal point.
        The default value is 0.
    """
    ...


@builtin_function(_row)
def row(obj: Constant, index: Constant) -> Constant:
    r"""Return one or more rows of a vector/matrix/table.

    Parameters
    ----------
    obj : Constant
        A vector/matrix/table.
    index : Constant
        An integral scalar or pair.
    """
    ...


@builtin_function(_rowAlign)
def rowAlign(left: Constant, right: Constant, how: Constant) -> Constant:
    r"""The rowAlign function aligns corresponding rows from left and right based
    on their values. It returns a tuple containing two elements (either array
    vectors or columnar tuples, matching the input type). Each element in this
    tuple contains indices that map the aligned elements to their original positions
    in left and right respectively. Unmatched elements from one input are marked
    as -1 in the other input's returned index.

    This function is typically used for aligning bid/ask prices, where left represents
    prices from one time point and right represents prices from a previous time point.
    The returned indices can be used with the rowAt function to extract the aligned
    elements from the original left and right arrays, with any unaligned elements left blank.

    Parameters
    ----------
    left : Constant
        An array vector or a columnar tuple.
    right : Constant
        An array vector or a columnar tuple.

        - left and right must be of the same data type and size (number of rows), but the number of elements in corresponding rows do not have to match. For example, if left has 3 rows and the first row has 5 elements, then right must also have 3 rows but the first row does not necessarily have 5 elements.

        - Data in each row of left and right must be strictly increasing/decreasing.
    how : Constant
        A string indicating how left and right will be aligned. It can take the following values:

        +----------+-----------------------------------------------------------------------------------------+-----------------------------------------+-----------------------------------------+
        | how      | Description                                                                             | Max. Value in the Alignment Result      | Min. Value in the Alignment Result      |
        +==========+=========================================================================================+=========================================+=========================================+
        | "bid"    | left and right are bid prices sorted in strictly decreasing order. The output will only | max(max(left), max(right))              | max(min(left), min(right))              |
        |          | include the indices of prices that fall within the alignment range.                     |                                         |                                         |
        +----------+-----------------------------------------------------------------------------------------+-----------------------------------------+-----------------------------------------+
        | "allBid" | left and right are bid prices sorted in strictly decreasing order. The output will      | max(max(left), max(right))              | min(min(left), min(right))              |
        |          | include the indices of all prices from left and right.                                  |                                         |                                         |
        +----------+-----------------------------------------------------------------------------------------+-----------------------------------------+-----------------------------------------+
        | "ask"    | left and right are ask prices sorted in strictly increasing order. The output will only | min(max(left), max(right))              | min(min(left), min(right))              |
        |          | include the indices of prices that fall within the alignment range.                     |                                         |                                         |
        +----------+-----------------------------------------------------------------------------------------+-----------------------------------------+-----------------------------------------+
        | "allAsk" | left and right are ask prices sorted in strictly increasing order. The output will      | max(max(left), max(right))              | min(min(left), min(right))              |
        |          | include the indices of all prices from left and right.                                  |                                         |                                         |
        +----------+-----------------------------------------------------------------------------------------+-----------------------------------------+-----------------------------------------+
    """
    ...


@builtin_function(_rowAnd)
def rowAnd(*args) -> Constant:
    r"""For each row (a vector is viewed as a one-column matrix here), return 1 if all rows of all input variables are true; otherwise return 0.
    """
    ...


@builtin_function(_rowAt)
def rowAt(X: Constant, Y: Constant = DFLT) -> Constant:
    r"""- If Y is not specified, X must be a Boolean matrix or Boolean array vector.
      The rowAt function retrieves the row indices for each "true" element in X by
      row and returns an array vector (or columnar tuple) of integers. The returned
      result has the same number of rows as X. If X contains a row with only null
      values or "false" elements, rowAt returns null for that row.

    - If Y is a vector of integers, then each element in Y indicates the column
      index for X at each row. The rowAt function retrieves the corresponding element
      at each row in X and returns a vector of the same size as Y. If no element is
      found at the position specified by Y, a null value is returned. When Y is a
      Boolean matrix, X must be a matrix.

    - If Y is a Boolean matrix or Boolean array vector (or columnar tuple), the
      rowAt function retrieves the elements in X that correspond to the "true"
      values in Y and returns an array vector (or columnar tuple). The returned
      result has the same number of rows as Y. For any row in Y that contains only
      "false" elements, rowAt returns a null value in the output array vector for that row.

    - If Y is an array vector (or columnar tuple) of integers, then each row in Y
      indicates the column index for X at each row. The rowAt function retrieves
      the corresponding element(s) at each row in X and returns an array vector
      (or columnar tuple) of the same dimension as Y. If no element is found at
      the position specified by Y, a null value is returned.

    Parameters
    ----------
    X : Constant
        A matrix/array vector/columnar tuple.
    Y : Constant, optional
        Can be a vector of integers, a Boolean matrix, a Boolean/integral array vector or columnar tuple.
    """
    ...


@builtin_function(_rowAvg)
def rowAvg(*args) -> Constant:
    r"""Calculate the average of each row of the arguments. A vector is viewed as
    a one-column matrix here.
    """
    ...


@builtin_function(_rowBeta)
def rowBeta(Y: Constant, X: Constant) -> Constant:
    r"""Calculate the coefficient estimate of the ordinary-least-squares
    regression of Y on X by row and return a vector with the same number of rows of X.

    Parameters
    ----------
    X : Constant
        A numeric vector/array vector.
    Y : Constant
        A numeric vector/array vector.
    """
    ...


@builtin_function(_rowCorr)
def rowCorr(X: Constant, Y: Constant) -> Constant:
    r"""Calculate the correlation between X and Y by row and return a vector with
    the same number of rows of X. Null values are ignored in calculation.

    Parameters
    ----------
    X : Constant
        A numeric vector/array vector.
    Y : Constant
        A numeric vector/array vector.
    """
    ...


@builtin_function(_rowCount)
def rowCount(*args) -> Constant:
    r"""Return the number of non-null elements in each row of the arguments.
    """
    ...


@builtin_function(_rowCovar)
def rowCovar(X: Constant, Y: Constant) -> Constant:
    r"""Calculate the covariance between X and Y by row and return a vector with
    the same number of rows of X.

    Parameters
    ----------
    X : Constant
        A numeric vector/array vector.
    Y : Constant
        A numeric vector/array vector.
    """
    ...


@builtin_function(_rowDenseRank)
def rowDenseRank(X: Constant, ascending: Constant = DFLT, ignoreNA: Constant = DFLT, percent: Constant = DFLT) -> Constant:
    r"""rowDenseRank can be viewed as function denseRank applied on rows instead
    of columns. It returns the consecutive rank of each element in each row.

    Parameters
    ----------
    X : Constant
        A matrix.
    ascending : Constant, optional
        A Boolean value indicating whether to sort in ascending order. The default value is true.
    ignoreNA : Constant, optional
        A Boolean value indicating whether null values are ignored in ranking and
        return NULL. When Null values participate in ranking, NULL values return 0,
        which is the smallest value in the result.
    percent : Constant, optional
        A Boolean value, indicating whether to display the returned rankings in
        percentile form. The default value is false.
    """
    ...


@builtin_function(_rowDot)
def rowDot(X: Constant, Y: Constant) -> Constant:
    r"""If both X and Y are vectors/matrices, calculate the inner product between
    X and Y by row. If both X and Y are indexed matrices, calculate the inner
    product between rows with the same label. For other rows, return NULL.

    For a vector and a matrix, the length of the vector must be the same as the number
    of columns of the matrix. Calculate the inner product between the vector and each
    row of the matrix is calculated.

    If X and Y are array vectors, calculate the inner product between the corresponding
    rows (vectors) in X and Y, i.e., dot(X.row(i),Y.row(i)).

    For a vector and an array vector, calculate the inner product between the vector
    and each vector in the array vector. Return NULL when X and Y are of different lengths.

    As with all other aggregate functions, null values are ignored in the calculation.

    Parameters
    ----------
    X : Constant
        A numeric vector/array vector.
    Y : Constant
        A numeric vector/array vector.
    """
    ...


@builtin_function(_rowEuclidean)
def rowEuclidean(X: Constant, Y: Constant) -> Constant:
    r"""If both X and Y are vectors/matrices, calculate the Euclidean distance
    between X and Y by row. If both X and Y are indexed matrices, calculate the
    Euclidean distance between rows with the same label. For other rows, return NULL.

    For a vector and a matrix, the length of the vector must be the same as the
    number of columns of the matrix. Calculate the Euclidean distance between the
    vector and each row of the matrix is calculated.

    If X and Y are array vectors, calculate the Euclidean distance between the
    corresponding rows (vectors) in X and Y, i.e., euclidean(X.row(i),Y.row(i)).

    For a vector and an array vector, calculate the Euclidean distance between
    the vector and each vector in the array vector. Return NULL when X and Y are of different lengths.

    As with all other aggregate functions, null values are ignored in the calculation.

    Parameters
    ----------
    X : Constant
        A numeric vector/array vector.
    Y : Constant
        A numeric vector/array vector.
    """
    ...


@builtin_function(_rowGroupby)
def rowGroupby(func: Constant, funcArgs: Constant, groupingCol: Constant, mode: Constant = DFLT, ascending: Constant = DFLT) -> Constant:
    r"""Group the data by groupingCol, then calculate func(funcArgs) and return a
    scalar for each group.

    Parameters
    ----------
    func : Constant
        An aggregate function.
    funcArgs : Constant
        The argument(s) passed to func. Multiple arguments can be represented in
        a tuple, and the dimension of each element must be consistent with groupingCol.
    groupingCol : Constant
        A non-empty matrix or array vector indicating the grouping column(s).
    mode : Constant, optional
        Specifies the returned data form. It can be:

        - "tuple" (default): Return a tuple of length 2, the first element of which is an
          array vector that stores the grouping variables, and the second element is an
          array vector that stores the result of applying funcArgs to func in each group.

        - "dict": Return a dictionary with a key-value pair. 'key' stores the grouping
          variables and 'value' stores the result of applying funcArgs to func in each group.

        - "table": Return a table with two columns. 'key' stores the grouping variables
          and 'value' stores the result of applying funcArgs to func in each group.
    ascending : Constant, optional
        A Boolean value indicating whether to sort the output by groupingCol in ascending or descending order. The default value is true.

    Returns
    -------
    Constant
        As specified in mode, sorted by groupingCol in ascending order.
    """
    ...


@builtin_function(_rowImax)
def rowImax(*args) -> Constant:
    r"""Return the index of the maximum in each row. If there are multiple maxima,
    return the index of the first maximum from the left. The result is a vector
    with the same length as the number of input rows.
    """
    ...


@builtin_function(_rowImaxLast)
def rowImaxLast(*args) -> Constant:
    r"""Return a vector of the same length as the number of rows of the argument.
    The vector contains the index of the element with the largest value in X in each row.
    If there are multiple elements with the identical largest value, return the index
    of the first element from the right.
    """
    ...


@builtin_function(_rowImin)
def rowImin(*args) -> Constant:
    r"""Return the index of the minimum in each row. If there are multiple minima,
    return the index of the first minimum from the left. The result is a vector
    with the same length as the number of input rows.
    """
    ...


@builtin_function(_rowIminLast)
def rowIminLast(*args) -> Constant:
    r"""Return a vector of the same length as the number of rows of the argument.
    The vector contains the index of the element with the smallest value in X in
    each row. If there are multiple elements with the identical smallest value,
    return the index of the first element from the right.
    """
    ...


@builtin_function(_rowKurtosis)
def rowKurtosis(X: Constant, biased: Constant = DFLT) -> Constant:
    r"""Return the kurtosis of each row in X.

    The calculation uses the following formula when biased=true:

    .. math::

        \begin{align*}
        \operatorname{kurtosis}(x) &=
        \frac{\displaystyle \frac{1}{n}\sum_{i=1}^n (x_i-\bar{x})^4}
        {\displaystyle\left(\frac{1}{n}\sum_{i=1}^n (x_i-\bar{x})^2\right)^2}
        \end{align*}

    Parameters
    ----------
    X : Constant
        A matrix, array vector, columnar tuple, or tuple with equal-length vectors.
    biased : Constant, optional
        A Boolean value, indicating whether the result is biased. The default
        value is true, meaning the bias is not corrected.
    """
    ...


@builtin_function(_rowMax)
def rowMax(*args) -> Constant:
    r"""Calculate the maximum value of each row of the arguments.
    """
    ...


@builtin_function(_rowMin)
def rowMin(*args) -> Constant:
    r"""Calculate the minimum value of each row of the arguments.
    """
    ...


@builtin_function(_rowMove)
def rowMove(X: Constant, steps: Constant) -> Constant:
    r"""The rowMove function shifts the elements in each row of X left or right by
    a specified number of steps.

    Parameters
    ----------
    X : Constant
        A matrix, array vector, columnar tuple, or tuple with equal-length vectors.
    steps : Constant
        An integer indicating the length to shift the row elements of X.

        - if steps is positive, the elements in each row are shifted to the right by steps position(s).

        - if steps is negative, the elements in each row are shifted to the left by steps position(s).

        - if steps is 0, X is not shifted.
    """
    ...


@builtin_function(_rowNames)
def rowNames(obj: Constant) -> Constant:
    r"""Return the row names of matrix X. Please check related function: columnNames.

    Parameters
    ----------
    obj : Constant
        A matrix.
    """
    ...


@builtin_function(_rowNext)
def rowNext(X: Constant) -> Constant:
    r"""For each row in X, rowNext shifts the elements to the left for one position.

    Parameters
    ----------
    X : Constant
        A matrix, array vector, columnar tuple, or tuple with equal-length vectors.
    """
    ...


@builtin_function(_rowNo)
def rowNo(X: Constant) -> Constant:
    r"""Return the index position of each row in a table.

    Parameters
    ----------
    X : Constant
        A matrix, array vector, columnar tuple, or tuple with equal-length vectors.
    """
    ...


@builtin_function(_rowOr)
def rowOr(*args) -> Constant:
    r"""For each row (a vector is viewed as a one-column matrix here), return 1
    if there are true elements in each row of the input; otherwise return 0.
    """
    ...


@builtin_function(_rowPrev)
def rowPrev(X: Constant) -> Constant:
    r"""For each row in X, rowPrev shifts the elements to the right for one position.

    Parameters
    ----------
    X : Constant
        A matrix, array vector, columnar tuple, or tuple with equal-length vectors.
    """
    ...


@builtin_function(_rowProd)
def rowProd(*args) -> Constant:
    r"""Calculate the product of each row of the arguments.
    """
    ...


@builtin_function(_rowRank)
def rowRank(X: Constant, ascending: Constant = DFLT, groupNum: Constant = DFLT, ignoreNA: Constant = DFLT, tiesMethod: Constant = DFLT, percent: Constant = DFLT, precision: Constant = DFLT) -> Constant:
    r"""Conduct the following operation within each row of matrix X:

    - Return the position of each element in the sorted vector.

    - If groupNum is specified, group the elements into groupNum groups and return the group number each element belongs to.

    - If ignoreNA =true, null values return NULL.

    The result is a matrix with the same shape as X.

    Parameters
    ----------
    X : Constant
        A matrix.
    ascending : Constant, optional
            Boolean value indicating whether the sorting is in ascending order.
            The default value is true (ascending).
    groupNum : Constant, optional
        A positive integer indicating the number of groups to sort X into.
    ignoreNA : Constant, optional
        A Boolean value indicating whether null values are ignored.
    tiesMethod : Constant, optional
        A string indicating how to rank the group of elements with the same value (i.e., ties):

        - 'min' : the smallest rank value of the tie values.

        - 'max' : the largest rank value of the tie values.

        - 'average' : the average of the rank values for all ties.

        - 'first': Gives the first found tie value the lowest rank value, and
          continues with the following rank value for the next tie.
    percent : Constant, optional
        A Boolean value, indicating whether to display the returned rankings in
        percentile form. The default value is false.
    precision : Constant, optional
        An integer between [1, 15]. If the absolute difference between two values
        is no greater than 10^(-precision), the two values are considered to be equal.

        .. note::

            If parameter precision is specified, X must be numeric, and the
            tiesMethod cannot be specified as 'first'.
    """
    ...


@builtin_function(_rowSize)
def rowSize(*args) -> Constant:
    r"""Calculate the number of elements (null values included) of each row.
    """
    ...


@builtin_function(_rowSkew)
def rowSkew(X: Constant, biased: Constant = DFLT) -> Constant:
    r"""Return the skewness of each row in X.

    The calculation uses the following formula when biased=true:

    .. math::

        \begin{align*}
        \operatorname{skew}(x) &= \frac{\dfrac{1}{n}\sum_{i=1}^n (x_i-\bar{x})^3}{\left(\sqrt{\dfrac{1}{n}\sum_{i=1}^n (x_i-\bar{x})^2}\right)^3}
        \end{align*}

    Parameters
    ----------
    X : Constant
        A matrix, array vector, columnar tuple, or tuple with equal-length vectors.
    biased : Constant, optional
        A Boolean value, indicating whether the result is biased. The default
        value is true, meaning the bias is not corrected.
    """
    ...


@builtin_function(_rowStd)
def rowStd(*args) -> Constant:
    r"""Calculate the (sample) standard deviation of each row of the arguments.
    """
    ...


@builtin_function(_rowStdp)
def rowStdp(*args) -> Constant:
    r"""Calculate the population standard deviation of each row.
    """
    ...


@builtin_function(_rowSum)
def rowSum(*args) -> Constant:
    r"""Calculate the sum of each row of the arguments.
    """
    ...


@builtin_function(_rowSum2)
def rowSum2(*args) -> Constant:
    r"""Calculate the sum of square of all elements in each row of the arguments.
    """
    ...


@builtin_function(_rowTanimoto)
def rowTanimoto(X: Constant, Y: Constant) -> Constant:
    r"""If both X and Y are vectors/matrices, calculate the tanimoto distance between
    X and Y by row. If both X and Y are indexed matrices, calculate the tanimoto
    distance between rows with the same label. For other rows, return NULL.

    For a vector and a matrix, the length of the vector must be the same as the
    number of columns of the matrix. Calculate the tanimoto distance between the
    vector and each row of the matrix.

    If X and Y are array vectors, calculate the tanimoto distance between the
    corresponding rows (vectors) in X and Y, i.e., tanimoto(X.row(i),Y.row(i)).

    For a vector and an array vector, calculate the tanimoto distance between the
    vector and each vector in the array vector. Return NULL when X and Y are of different lengths.

    As with all other aggregate functions, null values are ignored in the calculation.

    Parameters
    ----------
    X : Constant
        A numeric vector/array vector/matrix.
    Y : Constant
        A numeric vector/array vector/matrix.
    """
    ...


@builtin_function(_rowVar)
def rowVar(*args) -> Constant:
    r"""Calculate the (sample) variance of each row of the arguments.
    """
    ...


@builtin_function(_rowVarp)
def rowVarp(*args) -> Constant:
    r"""Calculate the population variance of each row.
    """
    ...


@builtin_function(_rowWavg)
def rowWavg(X: Constant, Y: Constant) -> Constant:
    r"""Calculate the weighted average of X by row with Y as the weights and return
    a vector with the same number of rows of X.

    Parameters
    ----------
    X : Constant
        A matrix, vector, or array vector.
    Y : Constant
        A matrix, vector, or array vector.
    """
    ...


@builtin_function(_rowWsum)
def rowWsum(X: Constant, Y: Constant) -> Constant:
    r"""For each row, return 1 if odd number of columns are true; otherwise return 0.

    Parameters
    ----------
    X : Constant
        A matrix, vector, or array vector.
    Y : Constant
        A matrix, vector, or array vector.


    ====================
    [rowXor]
    ====================
    """
    ...


@builtin_function(_rowXor)
def rowXor(*args) -> Constant:
    ...


@builtin_function(_rows)
def rows(obj: Constant) -> Constant:
    r"""Return the number of rows in X. Please check related function: cols.

    Parameters
    ----------
    obj : Constant
        A  vector/matrix/table.
    """
    ...


@builtin_function(_rpad)
def rpad(str: Constant, length: Constant, pattern: Constant = DFLT) -> Constant:
    r"""Pad the right-side of a string with a specific set of characters.

    Parameters
    ----------
    str : Constant
        A string scalar or vector. It is the string to pad characters to (the right-hand side).
    length : Constant
        A positive integer indicating the number of characters to return.
        If length is smaller than the length of str, the rpad function will
        truncate str to the size of length.
    pattern : Constant, optional
            string scalar. It is the string that will be padded to the right-hand
            side of str. If it is unspecified, the rpad function will pad spaces to
            the right-side of str.
    """
    ...


@builtin_function(_rshift)
def rshift(X: Constant, bits: Constant) -> Constant:
    r"""Shift bits to the right.

    Parameters
    ----------
    X : Constant
        An integral scalar/pair/vector/matrix.
    bits : Constant
        The number of bits to shift.
    """
    ...


@builtin_function(_rtrim)
def rtrim(X: Constant) -> Constant:
    r"""Take a string of characters that has spaces at the end, and return the text
    without the spaces at the end.

    Parameters
    ----------
    X : Constant
        A  string scalar or vector.
    """
    ...


@builtin_function(_sample)
def sample(partitionCol: Constant, size: Constant) -> Constant:
    r"""Must be used in a where clause. Take a random sample of a number of partitions in a partitioned table.

    Suppose the database has N partitions. If 0<size<1, then take int(N*size) partitions.
    If size is a positive integer, then take size partitions.

    Parameters
    ----------
    partitionCol : Constant
        A partitioning column.
    size : Constant
        A positive floating number or integer.
    """
    ...


@builtin_function(_saveAsNpy)
def saveAsNpy(obj: Constant, fileName: Constant) -> Constant:
    r"""Save a vector/matrix in DolphinDB as an npy file. It must be executed by a logged-in user.

    .. note::

        Null values in obj will be converted to negative infinity (-inf).

    Parameters
    ----------
    obj : Constant
        A numeric vector/matrix.
    fileName : Constant
        Tthe path and name of the output file.
    """
    ...


@builtin_function(_saveDatabase)
def saveDatabase(a: Constant) -> Constant:
    r"""Save a database handle. It must be executed by a logged-in user. It is used
    with the database function.

    After we create a database for the first time, we can save the database with
    the command saveDatabase. If the database location is a folder that already
    contains DolphinDB table related files, then function database reopens a
    previously created database, and there is no need to use the saveDatabase command to save it.

    Parameters
    ----------
    a : Constant
        A DolphinDB database handle.
    """
    ...


@builtin_function(_saveDualPartition)
def saveDualPartition(dbHandle1: Constant, dbHandle2: Constant, table: Constant, tableName: Constant, partitionColumn1: Constant, partitionColumn2: Constant, compression: Constant = DFLT) -> Constant:
    r"""Save a table in the local node before sharing it to other nodes to form a dual partition database. It must be executed by a logged-in user.

    It is used together with statement share. If the partition and a table already exist, the function will append the new data to the existing table.

    Parameters
    ----------
    dbHandle1 : Constant
        The database handle of the first level partition.
    dbHandle2 : Constant
        The database handle of the second level partition.
    table : Constant
        The table in memory to be saved.
    tableName : Constant
        A string indicating the desired name of the saved partitioned table.
    partitionColumn1 : Constant
        A string indicating the partitioning column of the first level partition.
    partitionColumn2 : Constant
        A string indicating the partitioning column of the second level partition.
    compression : Constant, optional
            Boolean variable. It sets the compression mode. When it is set to true,
            the table will be saved to disk in compression mode. The default value is false.
    """
    ...


@builtin_function(_saveModel)
def saveModel(model: Constant, file: Constant) -> Constant:
    r"""Save the specifications of a trained model to a file on disk.

    Parameters
    ----------
    model : Constant
        A dictionary of the specifications of a prediction model. It is generated
        by functions such as randomForestClassifier and randomForestRegressor.
    file : Constant
        A string indicating the absolute path and name of the output file.
    """
    ...


@builtin_function(_savePartition)
def savePartition(dbHandle: Constant, table: Constant, tableName: Constant, compression: Constant = DFLT, trans: Constant = DFLT) -> Constant:
    r"""Save a table as a partitioned DFS table. It must be executed by a logged-in user.

    An empty table must be created with the function createPartitionedTable.

    Parameters
    ----------
    dbHandle : Constant
        A DolphinDB database handle.
    table : Constant
        The table in memory to be saved.
    tableName : Constant
        Aa string indicating the desired name of the saved partitioned table.
    compression : Constant, optional
        A Boolean variable. It sets the compression mode. When it is set to true,
        the table will be saved to disk in compression mode, by default DFLT.
    """
    ...


@builtin_function(_saveTable)
def saveTable(dbHandle: Constant, table: Constant, tableName: Constant = DFLT, append: Constant = DFLT, compression: Constant = DFLT, trans: Constant = DFLT) -> Constant:
    r"""Save a table to an unpartitioned disk table. It must be executed by a logged-in user.

    To save a table to a partitioned database, use createPartitionedTable together with append_ or tableInsert.

    .. note::

        Disk tables are only used for backup or local computing. Unlike the DFS tables, disk tables do not support access control.n

    Parameters
    ----------
    dbHandle : Constant
        A DolphinDB database handle.
    table : Constant
        The table in memory to be saved.
    tableName : Constant, optional
        Aa string indicating the desired name for the saved table, by default DFLT.
    append : Constant, optional
        The appending mode, by default DFLT. When it is set to true, the new table
        will be appended to the old table.
    compression : Constant, optional
        The compression mode. When it is set to true, the table will be saved to
        disk in compression mode, by default DFLT.
    """
    ...


@builtin_function(_saveText)
def saveText(obj: Constant, filename: Constant, delimiter: Constant = DFLT, append: Constant = DFLT, header: Constant = DFLT, bom: Constant = DFLT) -> Constant:
    r"""Save DolphinDB variables or data queried by SQL statement as a text file
    on disk. Compared with saveTable, saveText requires more disk space and time.

    Parameters
    ----------
    obj : Constant
        Can be a table/matrix/vector/metacode of SQL statements. When obj is the
        metacode of SQL statements, multiple workers are allocated to read the
        data concurrently, and the data is written to the file with another worker.
        In other cases, data queries and writes are handled by the current worker.
    filename : Constant
        A string indicating the absolute path and name of the output file.
        Currently the output file can only be saved in .csv format.
    delimiter : Constant, optional
        The table column separator. The system uses comma as the default delimiter, by default DFLT.
    append : Constant, optional
        A Boolean value indicating whether to append to (true) or overwrite (false)
        the output file if it exists already, by default DFLT.
    header : Constant, optional
        A BOOLEAN indicating whether to save the column names in the output file
        when obj is a table, by default DFLT.
    bom : Constant, optional
        A case-insensitive STRING scalar that determines whether to include
        Byte order mark (BOM) in output CSV files. Currently, only "UTF-8" is
        supported, by default DFLT
    """
    ...


@builtin_function(_saveTextFile)
def saveTextFile(content: Constant, filename: Constant, append: Constant = DFLT, lastModified: Constant = DFLT) -> Constant:
    r"""Save strings to a file by appending or overwriting. It must be executed by a logged-in user.

    Parameters
    ----------
    content : Constant
        The contents to be written into the file.
    filename : Constant
        A string indicating the absolute path and name of the output file.
        Currently the output file can only be saved in .csv format.
    append : Constant, optional
        A Boolean flag. True means appending while false means overwriting, by default DFLT.
    lastModified : Constant, optional
        The previously modified time displayed in epoch time format, by default DFLT.
    """
    ...


@builtin_function(_schema)
def schema(table: Union[Alias[Literal["dbHandle"]], Constant]) -> Constant:
    r"""Display information about the schema of a table or a database.

    Parameters
    ----------
    table : Union[Alias[Literal[&quot;dbHandle&quot;]], Constant]
        Can be a table object or a database handle.

    Returns
    -------
    Constant
        An unordered dictionary containing the following information (in alphabetical order):

        - atomic: the level at which the atomicity is guaranteed for a write transaction. It can be TRANS or CHUNK.

        - chunkGranularity: the chunk granularity which determines whether to allow concurrent writes to different tables in the same chunk. It can be TABLE or DATABASE.

        - clusterReplicationEnabled: whether asynchronous replication has been enabled.

        - colDefs: information about each column in the table:

          - name: column name

          - typeString: column type

          - typeInt: the type ID

          - extra: the scale of a DECIMAL value

          - comment: comment on the column

          - sensitive: whether this column is set as a sensitive column. It is returned only when table is a DFS table.

        - compressMethods: the compression methods used for specified columns of a DFS table.

          - name: Column names

          - compressMethods: Compression algorithm applied, including "lz4", "delta", or "zstd".

        - databaseDir: the directory where the database is stored.

        - databaseOwner: the database creator.

        - dbUrl: path to the distributed database where the DFS table is located. It is returned only when table is a DFS table.

        - encryptMode: The table encryption mode specified during table creation. It is returned only when table is a DFS table.

        - engineType: the storage engine type. It can be OLAP or TSDB.

        - keepDuplicates: how to deal with records with duplicate sort key values.

        - keyColumn: key column(s) of the table. It is returned only when table contains key column(s).

        - partitionColumnIndex: the index that indicates the positions of partitioning columns. It returns -1 for a dimension table.

        - partitionColumnName: the partitioning column names.

        - partitionColumnType: the data type ID (which can be checked at Data Types and Data Forms) of the partitioning column.

        - partitionSchema: how the partitions are organized

        - partitionSites (optional): If the parameter locations is specified for function database, it displays the ip:port information of the specified node.

        - partitionTypeName / partitionType: the partitioning scheme and the corresponding ID, including VALUE(1), RANGE(2), LIST(3), COMPO(4), HASH(5).

        - sortColumns: the sort columns for a table.

        - softDelete: whether soft deletion of the table has been enabled. This field will only be returned for tables in TSDB databases. Return true if soft deletion has been enabled, false otherwise.

        - sortKeyMappingFunction: the mapping functions applied to sort keys.

        - tableComment: the comment for DFS tables.

        - tableName: table name. It is returned only when table is a DFS table.

        - tableOwner: the table creator.

        - partitionFunction: the function applied to a column for data partitioning. It is a STRING vector with each element as a function signature. If an element is "asis", meaning no function is applied to that column. For example, partitionFunction->["myPartitionFunc{, 6, 8}","asis"].

        - latestKeyCache: whether the latest value cache is enabled.

        - compressHashSortKey: whether the compression for sort columns is enabled.
    """
    ...


@builtin_function(_schur)
def schur(obj: Constant, sort: Constant = DFLT) -> Constant:
    r"""Compute the Schur decomposition of a square matrix.

    Suppose the input is the square matrix A:

    - If sort is not specified, return 2 matrices: T (Schur form of A, an upper triangular matrix)
      and an unitary matrix Z (the transpose matrix of Z is equal to its inverse matrix),
      so that A = Z*T*Z-1.

    - If sort is specified, the function will also return an integer indicating
      the number of eigenvalues that meet the sorting conditions.

    Parameters
    ----------
    obj : Constant
        A square matrix.
    sort : Constant, optional
        A string, by default DFLT.

        It is used to reorder the factors according to a specified ordering of the
        eigenvalues. The value can be 'lhp' (eigenvalue is a negative real number),
        'rhp' (eigenvalue is a positive real number), 'iuc' (the absolute value of a
        complex eigenvalue<=1.0), 'ouc' (the absolute value of a complex eigenvalue>1.0).
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_scs)
    def scs(f: Constant, P: Constant = DFLT, A: Constant = DFLT, b: Constant = DFLT, Aeq: Constant = DFLT, beq: Constant = DFLT, lb: Constant = DFLT, ub: Constant = DFLT, x0: Constant = DFLT, c: Constant = DFLT, eps: Constant = DFLT, alpha: Constant = DFLT) -> Constant:
        r"""Solve the following optimization problem for the objective function with given constraints:

        .. math::

            \min\limits_{x} x^T P x + f^T x \quad \text{such that} \quad
            \begin{cases}
            A \cdot x \le b \\
            A_{\mathrm{eq}} \cdot x = b_{\mathrm{eq}} \\
            \|x - x_0\| \le c \\
            lb \le x \le ub
            \end{cases}

        The result is a 2-element tuple. The first element is the minimum value of the objective function. The second element is the value of x when the value of the objective function is minimized.

        Parameters
        ----------
        f : Constant
            A vector of coefficients for linear terms in the quadratic programming problem.
            It must be of the same length as x0.
        P : Constant, optional
            A  matrix obtained by multiplying the diagonal elements of the coefficient
            matrix for quadratic terms by 2, by default DFLT.
        A : Constant, optional
            A coefficient matrix for linear inequality constraints. Its number
            of columns must be consistent with the size of x, by default DFLT.
        b : Constant, optional
            The right-hand vector for linear inequality constraints, by default DFLT.
        Aeq : Constant, optional
            Aa coefficient matrix for linear equality constraints. Its number of
            columns must be consistent with the size of x, by default DFLT.
        beq : Constant, optional
            The right-hand vector for linear equality constraints, by default DFLT.
        lb : Constant, optional
            A scalar or a vector of the same length as x, specifying the lower
            bound for variables, by default DFLT.

            - If lb is a scalar, all variables are subject to the same lower bound constraints.
              If lb is null, there are no lower bound constraints for x.

            - If lb is a vector, the elements of x are subject to the corresponding
              elements of lb. If a certain element in lb is null, the corresponding
              element in x has no lower bound constraint.
        ub : Constant, optional
            A scalar or a vector of the same length as x, specifying the upper
            bound for variables, by default DFLT.

            - If ub is a scalar, all variables are subject to the same upper bound constraints.
              If ub is null, there are no upper bound constraints for x.

            - If ub is a vector, the elements of x are subject to the corresponding
              elements of ub. If a certain element in ub is null, the corresponding
              element in x has no upper bound constraint.
        x0 : Constant, optional
            A vector of coefficients for absolute value inequality constraints, by default DFLT.
        c : Constant, optional
            A non-negative number representing the right-hand constant for absolute
            value inequality constraints, by default DFLT.
        eps : Constant, optional
            A positive floating-point number representing the solution precision, by default DFLT.
        alpha : Constant, optional
            A  positive floating-point number representing the relaxation parameter, by default DFLT.
        """
        ...


@builtin_function(_searchK)
def searchK(X: Constant, k: Constant) -> Constant:
    r"""Return the k-th smallest item ignoring null values.

    Parameters
    ----------
    X : Constant
        A vector.
    k : Constant
        An integer indicating the k-th smallest item.
    """
    ...


@builtin_function(_seasonalEsd)
def seasonalEsd(data: Constant, period: Constant, hybrid: Constant = DFLT, maxAnomalies: Constant = DFLT, alpha: Constant = DFLT) -> Constant:
    r"""Conduct anomaly detection with the Seasoned Extreme Studentized Deviate test (S-ESD).

    The result is a table of anomalies. It has 2 columns: column index records the
    subscript of anomalies in data, and column anoms are the anomaly values.

    Parameters
    ----------
    data : Constant
        A numeric vector.
    period : Constant
        An integer larger than 1 indicating the length of a time-series cycle.
    hybrid : Constant, optional
        A Boolean value indicating whether to use median and median absolute
        deviation to replace mean and standard deviation. The results are more
        robust if hybrid=true, by default DFLT.
    maxAnomalies : Constant, optional
        A positive integer or a floating number between 0 and 0.5, by default DFLT.

        - If maxAnomalies is a positive integer, it must be smaller than the size of data.
          It indicates the upper bound of the number of anomalies.

        - If maxAnomalies is a floating number between 0 and 0.5, the upper bound of the
          number of anomalies is int(size(data) * maxAnomalies).
    alpha : Constant, optional
        A positive number indicating the significance level of the statistical test.
        A larger alpha means a higher likelihood of detecting anomalies, by default DFLT
    """
    ...


@builtin_function(_second)
def second(X: Constant) -> Constant:
    r"""Return the corresponding second(s).

    Parameters
    ----------
    X : Constant
        An integer or temporal scalar/vector.
    """
    ...


@builtin_function(_secondOfMinute)
def secondOfMinute(X: Constant) -> Constant:
    r"""For each element in X, return a number from 0 to 59 indicating which
    second of the minute it falls in.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type TIME, SECOND, DATETIME, TIMESTAMP, NANOTIME or NANOTIMESTAMP.
    """
    ...


@builtin_function(_segment)
def segment(X: Constant, segmentOffset: Constant = DFLT) -> Constant:
    r"""Divide a vector into groups. Each group is composed of identical values
    next to each other. For example, [1,1,2,2,1,1,1] is divided into 3 groups:
    [1,1], [2,2] and [1,1,1].

    Parameters
    ----------
    X : Constant
        A vector.
    segmentOffset : Constant, optional
        A Boolean value, by default DFLT.

    Returns
    -------
    Constant
        Return a vector of the same length as X.

        - If segmentOffset=true, each element of the result is the index(in X) of the first element in each group.

        - If segmentOffset=false, each element of the result is its group number. Group numbers start from 0.
    """
    ...


@builtin_function(_segmentby)
def segmentby(func: Constant, funcArgs: Constant, segment: Constant) -> Constant:
    r"""segmentby is very similar to contextby except for how groups are determined.
    With contextby, a group includes all elements with the same value. With segmentby,
    only a block of equal value elements counts as a group. 2 blocks of equal value
    elements separated by different values are treated as 2 groups.

    Parameters
    ----------
    func : Constant
        A function.
    funcArgs : Constant
        The parameters of func. It is a tuple if there are more than 1 parameter of func.
    segment : Constant
        The grouping variable.
    """
    ...


@builtin_function(_sej)
def sej(leftTable: Constant, rightTable: Constant, matchingCols: Constant, rightMatchingCols: Constant = DFLT, leftFilter: Constant = DFLT, rightFilter: Constant = DFLT) -> Constant:
    r"""Semantically equi join

    Parameters
    ----------
    leftTable : Constant
        The table to be joined.
    rightTable : Constant
        The table to be joined.
    matchingCols : Constant
        A string scalar/vector indicating matching columns.
    rightMatchingCols : Constant, optional
        A string scalar/vector indicating all the matching columns in rightTable.
        This optional argument must be specified if at least one of the matching
        columns has different names in leftTable and rightTable. The joining column
        names in the result will be the joining column names from the left table, by default DFLT.
    leftFilter : Constant, optional
        Condition expressions used as filter conditions for the columns in the
        left and right tables. Use "and" or "or" to join multiple conditions, by default DFLT.
    rightFilter : Constant, optional
        Condition expressions used as filter conditions for the columns in the
        left and right tables. Use "and" or "or" to join multiple conditions, by default DFLT.

    Returns
    -------
    Constant
        A table.
    """
    ...


@builtin_function(_sem)
def sem(X: Constant) -> Constant:
    r"""Return unbiased (normalized by N-1) standard error of the mean over X .

    - If X is a matrix, calculate the standard error for each column and return a vector.

    - If X is a table, calculate the standard error of each column and return a table.

    Parameters
    ----------
    X : Constant
        A numeric vector/matrix/table.
    """
    ...


@builtin_function(_semiMonthBegin)
def semiMonthBegin(X: Constant, dayOfMonth: Constant = DFLT, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""Return the first day of the semi-month that X belongs to. Suppose X is the
    d-th day of the month:

    - If d < dayOfMonth: return the first day of the month.

    - If d >= dayOfMonth: return the dayOfMonth-th day of the month.

    If parameter offset is specified, the result is updated every n semi-months.
    The parameters offset and n must be specified together, and offset takes
    effect only when n > 1.

    Parameters
    ----------
    X : Constant
        A scalar/vector of data type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    dayOfMonth : Constant, optional
        A n integer between 2 and 27, by default DFLT.
    offset : Constant, optional
        A scalar of the same data type as X. It must be no greater than the
        minimum value of X, by default DFLT.
    n : Constant, optional
        A positive integer, by default DFLT.
    """
    ...


@builtin_function(_semiMonthEnd)
def semiMonthEnd(X: Constant, dayOfMonth: Constant = DFLT, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""Suppose X is the d-th day of the month:

    - If d < dayOfMonth: return the last day of the previous month.

    - If d >= dayOfMonth: return the dayOfMonth-th day of the current month.

    If parameter offset is specified, the result is updated every n semi-months.
    The parameters offset and n must be specified together, and offset takes
    effect only when n > 1.

    Parameters
    ----------
    X : Constant
        A scalar/vector of data type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    dayOfMonth : Constant, optional
        An integer between 2 and 27. The default value is 15, by default DFLT.
    offset : Constant, optional
        A scalar of the same data type as X. It must be no greater than the minimum
        value of X, by default DFLT.
    n : Constant, optional
        A positive integer, by default DFLT.
    """
    ...


@builtin_function(_seq)
def seq(start: Constant, end: Constant) -> Constant:
    r"""Returns a vector starting from start and ending at end. The step between
    two adjacent elements is 1.

    .. note::

        If both start and end are integral or temporal NULLs, the function returns an empty vector.

    Parameters
    ----------
    start : Constant
        An integer or a temporal value.
    end : Constant
        An integer or a temporal value.
    """
    ...


@builtin_function(_sessionWindow)
def sessionWindow(X: Constant, sessionGap: Constant) -> Constant:
    r"""The first session window starts at the first non-null value of X.
    Sequentially check whether the difference between each element in X and its
    previous adjacent element is less than sessionGap. If the difference is less
    than sessionGap, the session window remains open. Otherwise, the session window
    ends and a new session window is started from the current element. The value
    of the first element in each session window is used as its identifier. This
    function returns the identifier of the session window to which each element in X belongs.

    .. note::

        - For null values in X: If the first element of X is null, a null value is returned; otherwise, it returns the identifier of the window to which the previous non-null element belongs.

        - For out-of-order data: It will not be involved in the comparison and the identifier of the current window is returned directly.

    Parameters
    ----------
    X : Constant
        A n integral or temporal vector.
    sessionGap : Constant
        A positive integer indicating the gap between two sessions. Its unit is the same as the time precision of X.
    """
    ...


@builtin_function(_set)
def set(keyType: Union[Alias[Literal["keyObj"]], Constant], capacity: Constant = DFLT) -> Constant:
    r"""Return the corresponding set object of vector X .
    """
    ...


@builtin_function(_setColumnComment)
def setColumnComment(table: Constant, columnComments: Constant) -> Constant:
    r"""Add comments to columns of a DFS table or an MVCC table. Use function schema to view column comments.

    Parameters
    ----------
    table : Constant
        A DFS table or MVCC table.
    columnComments : Constant
        A dictionary. Its keys are table columns and values are comments for each column.
    """
    ...


@builtin_function(_setIndexedMatrix_)
def setIndexedMatrix_(X: Constant, on: Constant = DFLT) -> Constant:
    r"""Set the labels of the rows and columns of a matrix as the indexes.

    Parameters
    ----------
    X : Constant
        A matrix with row labels and column labels. Row labels and column labels
        must be monotonically increasing with no duplicate values.
    on : Constant, optional
        A Boolean value indicating the conversion between a matrix and an indexed
        matrix, by default DFLT.
    """
    ...


@builtin_function(_setIndexedSeries_)
def setIndexedSeries_(X: Constant, on: Constant = DFLT) -> Constant:
    r"""Convert a single column matrix with row labels into an indexed series.

    Parameters
    ----------
    X : Constant
        A matrix with row labels and only one column. The row labels must be
        monotonically increasing with no duplicate values.
    on : Constant, optional
        A Boolean value indicating the conversion between a matrix and an indexed
        series, by default DFLT.
    """
    ...


@builtin_function(_setRandomSeed)
def setRandomSeed(seed: Constant) -> Constant:
    r"""Set the random seed.

    Parameters
    ----------
    seed : Constant
        An integer indicating the random seed.
    """
    ...


@builtin_function(_setRetentionPolicy)
def setRetentionPolicy(dbHandle: Constant, retentionHours: Constant, retentionDimension: Constant = DFLT, hoursToColdVolume: Constant = DFLT) -> Constant:
    r"""Set the policy of data retention and tiered storage. The parameter retentionHours
    should be specified as large as possible for tiered storage to avoid deleting any data.

    Both data retention and tiered storage are partition-based. Therefore, the interval
    configured by retentionHours and hoursToColdVolume must be divisible by the
    granularity of the partition.

    The system will keep the data with the timestamp of the last retentionHours
    based on the system time: Data of the last hoursToColdVolume are stored in volumes;
    Data in [current time - hoursToColdVolumes - 10 days, current time - hoursToColdVolumes)
    are migrated to coldVolumes. If multiple paths are specified for coldVolumes,
    the data will be transferred randomly to one of the specified directories.

    For other data, only data in the range of [current time - retentionHours - 10 days,
    current time - retentionHours) are deleted. To delete the data outside the range,
    you can call function dropPartition.

    .. note::

        The function is only applied to a DFS database.

    Parameters
    ----------
    dbHandle : Constant
        A database handle. The data type of at least one of the partitioning
        columns of the database must be DATE or DATEHOUR.
    retentionHours : Constant
        A positive integer indicating the number of hours that data are kept.
    retentionDimension : Constant, optional
        An integer indicating the layer of the temporal partition, by default DFLT.
    hoursToColdVolume : Constant, optional
        positive integer indicating the number of hours that data are kept in volumes.
        Data stored in volumes will be migrated to the specified coldVolumes
        (configuration parameter) after hoursToColdVolume, by default DFLT.
    """
    ...


@builtin_function(_shape)
def shape(obj: Constant) -> Constant:
    r"""Return the dimension of a scalar/vector/matrix as a PAIR.

    Parameters
    ----------
    obj : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_shapiroTest)
def shapiroTest(X: Constant) -> Constant:
    r"""Conduct a Shapiro-Wilk test on X.

    Parameters
    ----------
    X : Constant
        A numeric vector indicating the sample for the test.

    Returns
    -------
    Constant
        A dictionary with the following keys:

        - method : "Shapiro-Wilk normality test"

        - pValue : p-value of the test

        - W : W-stat
    """
    ...


@builtin_function(_share)
def share(table: Constant, sharedName: Constant, database: Constant = DFLT, dbName: Constant = DFLT, partitionColumn: Constant = DFLT, readonly: Constant = DFLT) -> Constant:
    r"""If only table and sharedName are specified:

    - When table is a table, it is shared across all sessions with the specified shared name. Local objects including tables are invisible to other sessions. They need to be shared before they are visible to other sessions. The shared name must be different from all regular table names on all sessions. Data of a shared stream table cannot be deleted or updated, but data of a shared table (created with table or mvccTable) can be deleted or updated. Data inserts are allowed on all types of shared tables.

    - When table is a streaming engine, a lock is applied to the engine to allow concurrent writes.

    If all 5 parameters are used: populate a shard of a distributed table and share it across all sessions with a shared name. The sharding is based on the given partitioning column. Multiple share statements are used together to save a DFS table on multiple nodes.

    The rows of a shared stream table cannot be updated or deleted. In comparison, the rows of other shared tables can be updated or deleted.

    Note that it is not allowed to share a stream table multiple times by modifying the shared table name.

    Parameters
    ----------
    table : Constant
        The table or engine to be shared across all sessions.
    sharedName : Constant
        A string indicating the name to be used to refer to the shared table
        across all sessions, or the name of the DFS table to be shared.
    database : Constant, optional
        A database handle. When it is defined by the function database,
        it specifies the location of each partition, by default DFLT.
    dbName : Constant, optional
        A string indicating the distributed database name, by default DFLT.
    partitionColumn : Constant, optional
        The partitioning column of the DFS table, by default DFLT.
    readonly : Constant, optional
        TBoolean value indicating whether to share an ordinary/keyed/indexed
        in-memory table as a readonly table to improve query performance, by default DFLT.
    """
    ...


@builtin_function(_short)
def short(X: Constant) -> Constant:
    r"""Convert the input to the data type of SHORT.

    Parameters
    ----------
    X : Constant
        Can be of any data type.
    """
    ...


@builtin_function(_shuffle)
def shuffle(X: Constant) -> Constant:
    r"""Return a new vector/matrix after taking a shuffle on the data.

    Parameters
    ----------
    X : Constant
        A vector/matrix.
    """
    ...


@builtin_function(_shuffle_)
def shuffle_(obj: Constant) -> Constant:
    r"""Please refer to `shuffle`. The only difference between `shuffle` and `shuffle_`
    is that the latter assigns the result to X and thus changing the value of X after the execution.

    Parameters
    ----------
    obj : Constant
        A vector/matrix.
    """
    ...


@builtin_function(_signbit)
def signbit(X: Constant) -> Constant:
    r"""Detect the sign bit of the input value.

    Parameters
    ----------
    X : Constant
        A floating-point or integer scalar.

    Returns
    -------
    Constant
        true if X is negative, false otherwise.
    """
    ...


@builtin_function(_signum)
def signum(X: Constant) -> Constant:
    r"""Return 1 if X is positive; 0 if X is 0; -1 if X is negative; NULL if X is null.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix of numeric or Boolean value.
    """
    ...


@builtin_function(_sin)
def sin(X: Constant) -> Constant:
    r"""The sine function.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix.
    """
    ...


@builtin_function(_sinh)
def sinh(X: Constant) -> Constant:
    r"""The hyperbolic sine function.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix.
    """
    ...


@builtin_function(_size)
def size(obj: Constant) -> Constant:
    r"""For a vector/matrix, size returns the number of elements. In comparison, count returns the number of non-null elements.

    For an in-memory table, size returns the number of rows.

    Parameters
    ----------
    obj : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_skew)
def skew(X: Constant, biased: Constant = DFLT) -> Constant:
    r"""Return the skewness of X. The calculation skips null values.

    The calculation uses the following formulas in different cases:

    - When biased=true:

    .. math::

        \begin{align*}
        \operatorname{skew}(x) &= \frac{\tfrac{1}{n}\sum_{i=1}^n \bigl(x_i-\overline{x}\bigr)^3}{\Bigl(\sqrt{\tfrac{1}{n}\sum_{i=1}^n \bigl(x_i-\overline{x}\bigr)^2}\Bigr)^3}
        \end{align*}


    - When biased=false:

    .. math::

        \begin{align*}
        \operatorname{skew}(x) &= \frac{\sqrt{n(n-1)}}{\,n-2\,}\cdot
        \frac{\displaystyle\frac{1}{n}\sum_{i=1}^n (x_i-\bar{x})^3}
        {\left(\displaystyle\sqrt{\frac{1}{n}\sum_{i=1}^n (x_i-\bar{x})^2}\right)^3}
        \end{align*}

    If X is a matrix, calculate the skewness of each column of X and return a vector.

    If X is a table, calculate the skewness of each column of X and return a table.

    The skew function also supports querying partitioned tables and distributed tables with bias correction.

    Parameters
    ----------
    X : Constant
        A vector/matrix.
    biased : Constant, optional
        A Boolean value indicating whether the result is biased, by default DFLT.
    """
    ...


@builtin_function(_sleep)
def sleep(milliseconds: Constant) -> Constant:
    r"""Pause the application for X milliseconds.

    Parameters
    ----------
    milliseconds : Constant
        A non-negative scalar.
    """
    ...


@builtin_function(_slice)
def slice(obj: Constant, index: Union[Alias[Literal["rowIndex"]], Constant], colIndex: Constant = DFLT) -> Constant:
    r"""For slice(obj, index):

    - If obj is an array vector and

      - index is a scalar, it returns a vector indicating a column;

      - index is a vector, it returns an array vector of selected rows;

      - index is a pair, it returns an array vector of selected columns.

    - If obj is a matrix and

      - index is a scalar, it returns a vector indicating a column.

      - index is a vector or a pair, it returns a matrix of selected columns.

    - If obj is a table and

      - index is a scalar, it returns a dictionary indicating a row.

      - index is a vector or a pair, it returns a table of selected rows.

    For slice(obj, rowIndex, [colIndex]):

    - If obj is an array vector and

      - rowIndex and colIndex are both scalars, it returns a vector indicating a column;

      - rowIndex is a scalar and colIndex is a pair (or vise versa), it returns an array vector of selected rows and columns;

      - rowIndex and colIndex are both pair, it returns an array vector of selected rows and columns.

    - If obj is a matrix and

      - rowIndex and colIndex are both scalars, it returns a scalar indicating the value of specified element of the matrix.

      - rowIndex is a scalar and colIndex is a pair (or vise versa), it returns a submatrix of selected rows and columns.

      - rowIndex and colIndex are both vectors or pairs, it returns a submatrix of selected rows and columns.

    - If obj is a table and

      - rowIndex and colIndex are both scalars, return a scalar indicating the value of specified element of the table.

      - rowIndex is a scalar and colIndex is a pair (or vise versa), it returns a table of selected rows and columns.

      - rowIndex and colIndex are both vectors or pairs, it returns a table of selected rows and columns.

    .. note::

        - To get a particular row or column from a table, consider using function col or row.

        - When index, rowIndex or colIndex specifies the index range of an array vector or a matrix, if the values are not within [0, size(X)-1], the corresponding results are null values.

    Parameters
    ----------
    obj : Constant
        Can be an array vector, a matrix or a table.
    index : Union[Alias[Literal[&quot;rowIndex&quot;]], Constant]
        Can be scalar/vector/pair indicating the row index. If index,
        rowIndex is a pair, it indicates the range of index which is left-closed and right-open.
    colIndex : Constant, optional
        Can be scalar/vector/pair indicating the column index, by default DFLT.
        If colIndex is a pair, it indicates the range of index which is left-closed and right-open.
    """
    ...


@builtin_function(_sliceByKey)
def sliceByKey(table: Constant, rowKeys: Constant, colNames: Constant = DFLT, preserveOrder: Constant = DFLT) -> Constant:
    r"""Get the rows containing the specified values of the key columns from a keyed table or an indexed table. It is faster than the corresponding SQL statement.

    For a keyed table, rowKeys must contain values for all key columns.

    For an indexed table, rowKeys must contain values for the first n key columns.

    If colNames is not specified, return all columns.

    The data form of the result depends on colNames. If colNames is a scalar, return a vector; if colNames is a vector, return an in-memory table.

    Parameters
    ----------
    table : Constant
        A keyed table or indexed table.
    rowKeys : Constant
        A scalar/vector indicating the specified values of key columns.
    colNames : Constant, optional
        A tring scalar/vector indicating the names of columns to be selected, by default DFLT.
    preserveOrder : Constant, optional
        A Boolean scalar indicating whether the result should maintain the input
        order of rowKeys, by default DFLT.
    """
    ...


@builtin_function(_sma)
def sma(X: Constant, window: Constant) -> Constant:
    r"""Calculate the Simple Moving Average (sma) for X in a sliding window of the given length.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    window : Constant
        A positive integer indicating the size of the sliding window.
    """
    ...


@builtin_function(_snippet)
def snippet(obj: Constant) -> Constant:
    r"""Print the results.

    Parameters
    ----------
    obj : Constant
        Can be data of any type.

    Returns
    -------
    Constant
        A STRING scalar.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_socp)
    def socp(f: Constant, G: Constant = DFLT, h: Constant = DFLT, l: Constant = DFLT, q: Constant = DFLT, A: Constant = DFLT, b: Constant = DFLT) -> Constant:
        r"""Solve SOCP problems and calculate the minimum of the objective function
        under specified constraints. The standard form of the SOCP constraint is as follows:

        .. math::

            \begin{align*}
            \text{minimize}\quad & f^T x\\
            \text{subject to}\quad & \|A_i x + b_i\|_2 \le c_i^T x + d_i,\quad i=1,\dots,m,\\
            & A x = b
            \end{align*}

        G is as follows:

        .. math::

            \begin{align*}
            \big[ -c_0 \;|\; -A_0^{T} \;|\; \dots \;|\; -c_i \;|\; -A_i^{T} \;|\; \dots \big]^{T}
            \end{align*}


        h is as follows:

        .. math::

            \begin{align*}
            [d_0 \mid b_0 \mid \dots \mid d_i \mid b_i \mid \dots]^{T}
            \end{align*}


        Parameters
        ----------
        f : Constant
            A numeric vector indicating the coefficient vector of the objective function.
        G : Constant, optional
            A numeric matrix indicating the coefficient matrix of the cone constraint,
            by default DFLT.
        h : Constant, optional
            A numeric vector indicating the right-hand-side vector of the cone
            constraint, by default DFLT.
        l : Constant, optional
            An integral scalar indicating the dimension of the non-negative
            quadrant constraint, by default DFLT.
        q : Constant, optional
            A positive vector indicating the dimension size of each second-order
            cone constraint. The form is [r0,r1,…,rN-1], by default DFLT.
        A : Constant, optional
            A numeric matrix indicating the coefficient matrix of the equality
            constraint, by default DFLT.
        b : Constant, optional
            A numeric vector indicating the right-hand-side vector of the equality
            constraint, by default DFLT.

        Returns
        -------
        Constant
            A 3-element tuple:

            - The first element is a string indicating the state of the solution:

              - Problem solved to optimality: optimal solution found;

              - Found certificate of primal infeasibility: no feasible solution to the primal;

              - Found certificate of dual infeasibility: no feasible solution to the dual;

              - Offset exitflag at inaccurate results: inaccurate results;

              - Maximum number of iterations reached: reach the maximum number of iterations;

              - Search direction unreliable: unreliable search direction;

              - Unknown problem in solver: the solver cannot identify the problem.

            - The second element is the value of x where the value of the objective function is minimized.

            - The third element is the minimum value of the objective function.
        """
        ...


if not sw_is_ce_edition():
    @builtin_function(_solve)
    def solve(X: Constant, Y: Constant) -> Constant:
        r"""It generates the vector b that solves X*b=Y.

        Parameters
        ----------
        X : Constant
            A square matrix.
        Y : Constant
            A vector.
        """
        ...


@builtin_function(_sort)
def sort(X: Constant, ascending: Constant = DFLT) -> Constant:
    r"""Return a sorted vector/matrix in ascending/descending order.

    Parameters
    ----------
    X : Constant
        A vector/matrix.
    ascending : Constant, optional
        A Boolean scalar indicating whether to sort X in ascending order or d
        escending order, by default DFLT.
    """
    ...


@builtin_function(_sort_)
def sort_(obj: Constant, ascending: Constant = DFLT) -> Constant:
    r"""Sort X in-place in ascending/descending order.

    Parameters
    ----------
    obj : Constant
        A vector/matrix.
    ascending : Constant, optional
        A Boolean scalar indicating whether to sort X in ascending order or
        descending order, by default DFLT.
    """
    ...


@builtin_function(_sortBy_)
def sortBy_(table: Constant, sortColumns: Constant, sortDirections: Constant = DFLT) -> Constant:
    r"""Sort a table in-place based on the specified columns and directions.
    If the table is a partitioned table, the sorting is conducted within each
    partition, not on the entire table.

    This operation is executed in parallel if the table is a partitioned table and
    the parallel processing feature is enabled (when the configuration parameter localExcutors > 0).

    Parameters
    ----------
    table : Constant
        A table object. It can be a partitioned or unpartitioned in-memory table.
    sortColumns : Constant
        A string scalar/vector indicating the columns based on which the table
        will be sorted. It can also be a piece of metacode with an expression.
    sortDirections : Constant, optional
        A Boolean scalar/vector indicating the sorting directions for the sorting
        columns, by default DFLT.

        1 means ascending and 0 means descending. If sortColumns is a vector and
        sortDirections is a scalar, the sortDirections applies to all the sorting columns.
    """
    ...


@builtin_function(_spearmanr)
def spearmanr(X: Constant, Y: Constant) -> Constant:
    r"""Calculate the Spearman rank correlation coefficient of X and Y.
    Null values are ignored in the calculation. Spearman correlation is a
    non-parametric measure of the monotonicity of the relationship between two
    data sets. The coefficient varies between -1 and +1, where 0 means no correlation.
    -1 or +1 means an exact monotonic relationship.

    If X or Y is a matrix, apply the function to each column and return a vector.

    Parameters
    ----------
    X : Constant
        A vector/ matrix.
    Y : Constant
        A vector/ matrix.
    """
    ...


@builtin_function(_splev)
def splev(X: Constant, tck: Constant) -> Constant:
    r"""splev, short for Spline Evaluation, is used to evaluate B-spline curves
    or their derivatives. Given the knots and coefficients of the B-spline representation,
    this function calculates the values of the smooth polynomials and their derivatives.
    If null value is included in the input values of x or tck, it will be filled with 0.

    Parameters
    ----------
    X : Constant
        A  vector that specifies a set of data points to obtain corresponding values on the spline.
    tck : Constant
        A tuple of length 3 or a B-spline curve object that contains a vector t
        of knots, the B-spline coefficients, and the degree k of the spline.
        It can be generated with function splrep. Note that the spline degree k
        must satisfy 1 <= k <= 5.

    Returns
    -------
    Constant
        y, a DOUBLE type vector that represents the array of spline function
        values evaluated at points x.
    """
    ...


@builtin_function(_spline)
def spline(X: Constant, Y: Constant, resampleRule: Constant, closed: Constant = DFLT, origin: Constant = DFLT, outputX: Constant = DFLT) -> Constant:
    r"""Resample X based on the specified resampleRule, closed and origin. Perform cubic spline interpolation on Y based on the resampled X.

    If outputX is unspecified, return a vector of Y after the interpolation.

    If outputX=true, return a tuple where the first element is the vector of resampled X and the second element is a vector of Y after the interpolation.

    Parameters
    ----------
    X : Constant
        A strictly increasing vector of temporal type.
    Y : Constant
        A numeric vector of the same length as X.
    resampleRule : Constant
        A string. See the parameter rule of function resample for the optional values.
    closed : Constant, optional
        A string indicating which boundary of the interval is closed, by default DFLT.

        - The default value is 'left' for all values of rule except for 'M', 'A', 'Q', 'BM', 'BA', 'BQ', and 'W' which all have a default of 'right'.

        - The default is 'right' if origin is 'end' or 'end_day'.
    origin : Constant, optional
        A string or a scalar of the same data type as X, indicating the timestamp
        where the intervals start, by default DFLT. It can be 'epoch', start',
        'start_day', 'end', 'end_day' or a user-defined time object.

        - 'epoch': origin is 1970-01-01

        - 'start': origin is the first value of the timeseries

        - 'start_day': origin is 00:00 of the first day of the timeseries

        - 'end': origin is the last value of the timeseries

        - 'end_day': origin is 24:00 of the last day of the timeseries
    outputX : Constant, optional
        A Boolean value indicating whether to output the resampled X, by default DFLT.
    """
    ...


@builtin_function(_split)
def split(str: Constant, delimiter: Constant = DFLT) -> Constant:
    r"""- str is a scalar:

      - If delimiter is not specified, split str into a CHAR vector.

      - If delimiter is specified, use delimiter as the delimiter to split str into a CHAR vector or a STRING vector.

    - str is a vector: Split each element of the vector as described above. Return the results in a columnar tuple.

    Parameters
    ----------
    str : Constant
        A TRING scalar or vector.
    delimiter : Constant, optional
        A CHAR or STRING scalar indicating the separator, by default DFLT. It can
        consist of one or more characters, with the default being a comma (',').
    """
    ...


@builtin_function(_splrep)
def splrep(X: Constant, Y: Constant, t: Constant = DFLT) -> Constant:
    r"""splrep, short for Spline Representation, is used to find the B-spline
    representation of a one-dimensional curve. With a given set of data points (x[i], y[i]),
    it determines the degree-3 smooth spline approximation over the
    interval x[0] <= x <= x[size(x)-1]. If null value is included in the input
    values of x, y, or t, it will be filled with 0.

    Parameters
    ----------
    X : Constant
        A vector of Integral/Temporal/Floating/Decimal type that define the data
        points for the cubic spline curve y = f(x).
    Y : Constant
        A vector of Integral/Temporal/Floating/Decimal type that define the data
        points for the cubic spline curve y = f(x).
    t : Constant, optional
        A vector indicating the knots needed. Splines can have different polynomials
        on either side of the knots, by default DFLT.

        The values in t must satisfy the Schoenberg-Whitney conditions, meaning
        there must exist a subset of data points x[j] for all j=0, 1,...,n-5
        such that t[j] < x[j] < t[j+4].

    Returns
    -------
    Constant
        A tuple of length 3 containing the vector of knots, the B-spline
        coefficients, and the degree of the spline.
    """
    ...


@builtin_function(_sql)
def sql(select: Constant, from_: Constant, where: Constant = DFLT, groupBy: Constant = DFLT, groupFlag: Constant = DFLT, csort: Constant = DFLT, ascSort: Constant = DFLT, having: Constant = DFLT, orderBy: Constant = DFLT, ascOrder: Constant = DFLT, limit: Constant = DFLT, hint: Constant = DFLT, exec: Constant = DFLT, map: Constant = DFLT) -> Constant:
    r"""Create a SQL statement dynamically. To execute the generated SQL statement, use function eval.

    Parameters
    ----------
    select : Constant
        A metacode indicating the columns to be selected. Each column is generated
        by either function sqlCol or sqlColAlias . Use a tuple to select multiple columns.
    from_ : Constant
        A table object or table name.
    where : Constant, optional
        Indicates the "where" conditions. In case of multiple "where" conditions,
        use an ANY vector with each element corresponding to the metacode of a
        condition, by default DFLT.
    groupBy : Constant, optional
        Indicates "group by" or "context by" column(s). In case of multiple
        "group by" columns, use an ANY vector with each element corresponding to
        the metacode of a column name, by default DFLT.
    groupFlag : Constant, optional
        1 means "group by"; 0 means "context by"; 2 means "pivot by", by default DFLT.
    csort : Constant, optional
        A metacode or a tuple of metacode that specifies the column name(s) followed
        by csort, by default DFLT. This parameter only works when contextBy is specified.
    ascSort : Constant, optional
        A scalar or vector indicating whether each csort column is sorted in
        ascending or descending order, by default DFLT. 1 (default) means ascending
        and 0 means descending.
    having : Constant, optional
        A metacode or a tuple of metacode that specifies the having condition(s),
        by default DFLT. This parameter only works when contextBy is specified.
    orderBy : Constant, optional
        Indicates "order by" column(s). In case of multiple "order by" columns,
        use a tuple with each element corresponding to the metacode of a column
        name, by default DFLT.
    ascOrder : Constant, optional
        A scalar or vector indicating whether each "order by" column is sorted
        in ascending or descending order, by default DFLT. 1 means sorting in
        ascending order; 0 means sorting in descending order.
    limit : Constant, optional
        An integer or an integral pair indicating the number of rows to select
        from the result starting from the first row, by default DFLT. If groupBy
        is specified and groupFlag=0, select limit rows from each group starting
        from the first row in each group. It corresponds to "top" clause in "select" statements.

        - If limit is a integer n, it returns the first n rows.

        - If limit is a pair "start:end", it returns rows from the start-th row (inclusive) to the end-th row (exclusive).

        If groupBy is specified and groupFlag = 0, the limit is applied within each group independently.
    hint : Constant, optional
        A constant that can take the following values:

        - HINT_HASH: use Hashing algorithm to execute "group by" statements.

        - HINT_SNAPSHOT: query data from snapshot engine.

        - HINT_KEEPORDER: the records in the result after executing "context by"
          statements are in the same order as in the input data.
    exec : Constant, optional
        Indicates whether to use the exec clause, by default DFLT.

        If set to be true, a scalar or a vector will be generated. If the
        "pivot by" is used in the exec clause, a matrix can be generated.
    map : Constant, optional
        A Boolean scalar specifying whether to use the map keyword, by default DFLT.
    """
    ...


@builtin_function(_sqlCol)
def sqlCol(colName: Constant, func: Constant = DFLT, alias: Constant = DFLT, qualifier: Constant = DFLT) -> Constant:
    r"""Generate metacode for selecting one or multiple columns with or without calculations.
    It is generally used together with function sql and eval to generate SQL statements dynamically.

    Parameters
    ----------
    colName : Constant
        A string scalar/vector indicating column name(s).
    func : Constant, optional
        A unary function, by default DFLT.
    alias : Constant, optional
        A string scalar/vector indicating column name(s) of the selected column(s)
        or calculation result(s), by default DFLT.
    qualifier : Constant, optional
        A STRING scalar, by default DFLT. It is only used in a table join operation
        when we need to select a column that appears in both tables and that is
        not a matching column. It indicates the table from which to select the column.
    """
    ...


@builtin_function(_sqlColAlias)
def sqlColAlias(colDefs: Constant, colNames: Constant = DFLT) -> Constant:
    r"""Use metacode and an optional alias name to define a column. It is often used to name calculated columns.

    Parameters
    ----------
    colDefs : Constant
        A metacode.
    colNames : Constant, optional
        A string indicating an alias name, by default DFLT.
    """
    ...


@builtin_function(_sqlDS)
def sqlDS(sqlObj: Constant, forcePartition: Constant = DFLT) -> Constant:
    r"""Create a list of data sources based on the input SQL metacode. If the table
    in the SQL metacode has n partitions, sqlDS generates n data sources. If the
    SQL metacode doesn't contain any partitioned table, sqlDS returns a tuple
    containing one data source. This function divides a large file into several
    partitions, each representing a subset of the data, and returns a tuple of
    the data source. A data source is generally represented by a code object and
    serves as a function call that takes metaprogramming as its parameter and returns a table.

    Parameters
    ----------
    sqlObj : Constant
        SQL metacode. For more details about metacode please refer to the section of Metaprogramming.
    forcePartition : Constant, optional
        A Boolean value, by default DFLT. If it is set to false, the system checks
        if the query can be splitted into multiple child queries. If not then it
        won't split the query over partitions and will throw an exception.

        However, when it is set to true, the system splits the query over partitions
        and runs the query on selected partitions. Cases when a query cannot be
        splitted into child queries include (1) the group by columns are not
        partitioning columns; (2) the order by clause is specified, among others.
    """
    ...


@builtin_function(_sqlDelete)
def sqlDelete(table: Constant, where: Constant = DFLT, from_: Constant = DFLT) -> Constant:
    r"""Dynamically generate a metacode of the SQL delete statement. To execute
    the generated metacode, please use function eval.

    Parameters
    ----------
    table : Constant
        Can be an in-memory table or a DFS table.
    where : Constant, optional
        A metacode indicating the where condition, by default DFLT.
    from_ : Constant, optional
        A metacode indicating the from clause, which supports specifying table
        joins using ej or lj, by default DFLT.
    """
    ...


@builtin_function(_sqlUpdate)
def sqlUpdate(table: Constant, updates: Constant, from_: Constant = DFLT, where: Constant = DFLT, contextBy: Constant = DFLT, csort: Constant = DFLT, ascSort: Constant = DFLT, having: Constant = DFLT) -> Constant:
    r"""Dynamically generate a metacode of the SQL update statement.
    To execute the generated metacode, please use function eval.

    Parameters
    ----------
    table : Constant
        Can be an in-memory table or a distributed table.
    updates : Constant
        A metacode or a tuple of metacode, indicating the updating operation.
    from_ : Constant, optional
        A metacode indicating the table join operation, by default DFLT.
    where : Constant, optional
        A metacode indicating the where condition, by default DFLT.
    contextBy : Constant, optional
        A metacode indicating the context by clause, by default DFLT.
    csort : Constant, optional
        A metacode or a tuple of metacode that specifies the column name(s)
        followed by csort, by default DFLT. This parameter only works when contextBy is specified.
    ascSort : Constant, optional
        A scalar or vector indicating whether each csort column is sorted in
        ascending or descending order, by default DFLT. 1 (default) means ascending
        and 0 means descending.
    having : Constant, optional
        A metacode or a tuple of metacode that specifies the having condition(s), by default DFLT.
        This parameter only works when contextBy is specified.
    """
    ...


@builtin_function(_sqrt)
def sqrt(X: Constant) -> Constant:
    r"""Return the square root of each element in X. The data type of the result
    is always DOUBLE.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix.
    """
    ...


@builtin_function(_square)
def square(X: Constant) -> Constant:
    r"""Return the square of X. The data type of the result is always DOUBLE.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix.
    """
    ...


@builtin_function(_startsWith)
def startsWith(X: Constant, str: Constant) -> Constant:
    r"""Check if X starts with str. If yes, return true; otherwise return false.

    Parameters
    ----------
    X : Constant
        A string scalar/vector.
    str : Constant
        A string scalar.
    """
    ...


@builtin_function(_stat)
def stat(X: Constant) -> Constant:
    r"""Return a dictionary about the descriptive statistics of X including avg(mean),
    max, min, count, median, and stdev.

    Parameters
    ----------
    X : Constant
        A vector/matrix.
    """
    ...


@builtin_function(_stateIterate)
def stateIterate(X: Constant, initial: Constant, initialWindow: Constant, iterateFunc: Constant, combineCoeff: Constant) -> Constant:
    r"""Supposing the iteration is based only on the previous result, for the k-th (k ∈ N+) record,
    the calculation logic is (where the column "factor" holds the results):

    - k < initialWindow: factor[k] = initial[k]

    - k >= initialWindow:factor[k] = combineCoeff[0] * X[k] + combineCoeff[1] * iterateFunc(factor)[k-1]

    If iterateFunc is a window function, the iteration is based on multiple previous results.

    Parameters
    ----------
    X : Constant
        A a vector. It can be a column from the engine's input table,
        or the result of a vectorized function with the column as its input argument.
    initial : Constant
        A vector used to fill the first initialWindow values in the corresponding
        result column of the engine's output table. It can be a column from the
        engine's input table, or the result of a vectorized function with the
        column as its input argument.
    initialWindow : Constant
        A positive integer determining the initial window size [0, initialWindow).
    iterateFunc : Constant
        Tthe function for iteration, whose only parameter is the column from the output table.
        Currently, only the following functions are supported (use partial application
        to specify functions with multiple parameters):
        - Moving functions: tmove, tmavg, tmmax, tmmin, tmsum, mavg, mmax, mmin, mcount, msum

        - Cumulative window functions: cumlastNot, cumfirstNot

        - Order-sensitive functions: ffill, move

        .. note::

            - As the iterations are performed based on the historical data, the output for the current record is calculated based on the historical results in the output table and X.

            - When calculating with time-based moving windows, windows are determined by the current timestamp T, and the interval is (T - window, T).
    combineCoeff : Constant
        A ector of length 2. The elements indicate the correlation coefficients between the result of interateFunc and X.
    """
    ...


@builtin_function(_std)
def std(X: Constant) -> Constant:
    r"""If X is a vector, return the (unbiased) sample standard deviation of X.

    If X is a matrix, calculate the (unbiased) sample standard deviation of each
    column of X and return a vector.

    If X is a table, calculate the (unbiased) sample standard deviation of each
    column of X and return a table.

    As with all aggregate functions, null values are not included in the calculation.

    .. note::

        The result is sample standard deviation instead of population standard deviation.

    Parameters
    ----------
    X : Constant
        A  scalar/vector/matrix/table.
    """
    ...


@builtin_function(_stdp)
def stdp(X: Constant) -> Constant:
    r"""If X is a vector, return the population standard deviation of X.

    If X is a matrix, calculate the population standard deviation of each column and return a vector.

    If X is a table, calculate the population standard deviation of each column and return a table.

    As with all other aggregate functions, null values are not included in the calculation.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    """
    ...


@builtin_function(_stl)
def stl(data: Constant, period: Constant, sWindow: Constant, sDegree: Constant = DFLT, sJump: Constant = DFLT, tWindow: Constant = DFLT, tDegree: Constant = DFLT, tJump: Constant = DFLT, lWindow: Constant = DFLT, lDegree: Constant = DFLT, lJump: Constant = DFLT, robust: Constant = DFLT, inner: Constant = DFLT, outer: Constant = DFLT) -> Constant:
    r"""Use Loess method to decompose a time series into trend, seasonality and
    randomness. The result is a dictionary with the following keys: trend,
    seasonal, and residual. Each key corresponds to a vector with the same length as data.

    Parameters
    ----------
    data : Constant
        A numeric vector.
    period : Constant
        Ainteger larger than 1 indicating the length of a time-series cycle.
    sWindow : Constant
        Either the string "periodic" that means smoothing is effectively replaced
        by taking the mean, or an odd number no smaller than 7 indicating the
        span (in lags) of the loess window for seasonal extraction.
    sDegree : Constant, optional
        Can be 0, 1 or 2 indicating the degree of locally-fitted polynomial in
        seasonal extraction, by default DFLT
    sJump : Constant, optional
        An integer greater than 1 indicating the number of elements to skip for
        the smoother in seasonal extraction, by default DFLT.
    tWindow : Constant, optional
        A positive odd number indicating the span (in lags) of the loess window
        for trend extraction, by default DFLT.
    tDegree : Constant, optional
        Can be 0, 1 or 2 indicating the degree of locally-fitted polynomial in
        trend extraction, by default DFLT.
    tJump : Constant, optional
        An integer greater than 1 indicating the number of elements to skip for
        the smoother in trend extraction, by default DFLT
    lWindow : Constant, optional
        A positive odd number indicating the the span (in lags) of the loess
        window of the low-pass filter used for each subseries, by default DFLT.
    lDegree : Constant, optional
        Can be 0, 1 or 2 indicating the degree of locally-fitted polynomial for
        the subseries low-pass filter, by default DFLT.
    lJump : Constant, optional
        An integer greater than 1 indicating the number of elements to skip for
        the smoother in the subseries low-pass filter, by default DFLT.
    robust : Constant, optional
        A Boolean value indicating if robust fitting is used in the loess procedure, by default DFLT
    inner : Constant, optional
        A positive integer indicating the number of 'inner' (backfitting) iterations;
        usually very few (2) iterations suffice, by default DFLT.
    outer : Constant, optional
        A positive integer indicating the number of 'outer' robustness iterations, by default DFLT.
    """
    ...


@builtin_function(_strReplace)
def strReplace(str: Constant, pattern: Constant, replacement: Constant) -> Constant:
    r"""Return a copy of str and replace all occurrences of pattern with replacement.

    Parameters
    ----------
    str : Constant
        A string scalar/vector.
    pattern : Constant
        A string scalar/vector.
    replacement : Constant
        A string scalar/vector.
    """
    ...


@builtin_function(_streamTable)
def streamTable(*args) -> Constant:
    r"""Create a table in real-time mode to be used in streaming (also called a stream table).
    A table in real-time mode can handle concurrent reading and writing.
    """
    ...


@builtin_function(_stretch)
def stretch(X: Constant, n: Constant) -> Constant:
    r"""- If X is a vector or tuple, stretches X evenly to a new vector or tuple with the length of n.

    - If X is a matrix or table, stretches X evenly to a new matrix or table with n rows.

    The difference between stretch and take lies in:

    - take takes n values iteratively and sequentially from a vector, whereas stretch copies each element of the vector to stretch the vector to a new length n.

    Parameters
    ----------
    X : Constant
        A vector/tuple/matrix/table.
    n : Constant
        A non-negative integer.
    """
    ...


@builtin_function(_string)
def string(X: Constant) -> Constant:
    r"""Convert X to a string.

    Parameters
    ----------
    X : Constant
        Can be of any data type.
    """
    ...


@builtin_function(_stringFormat)
def stringFormat(format: Constant, *args) -> Constant:
    r"""stringFormat formats strings by replacing placeholders with values passed by the user.
    Formatting options (e.g. field width, precision, alignment) can be specified for more
    precise control over how the values are formatted in the output strings.

    Table 1. Supported data types

    +----------------+-------------------------+------------------------------------------------------------+
    | Type           | Placeholder (%-format)  | Examples of args                                           |
    +================+=========================+============================================================+
    | BOOL           | %b                      | 1b, 0b, true, false                                        |
    +----------------+-------------------------+------------------------------------------------------------+
    | CHAR           | %c                      | 'a', 97c                                                   |
    +----------------+-------------------------+------------------------------------------------------------+
    | SHORT          | %h                      | 122h                                                       |
    +----------------+-------------------------+------------------------------------------------------------+
    | INT (integer)  | %i                      | 21                                                         |
    +----------------+-------------------------+------------------------------------------------------------+
    | Octal          | %o                      | 31                                                         |
    +----------------+-------------------------+------------------------------------------------------------+
    | Hexadecimal    | %x (lowercase)          | 2f                                                         |
    +----------------+-------------------------+------------------------------------------------------------+
    | Hexadecimal    | %X (uppercase)          | 2F                                                         |
    +----------------+-------------------------+------------------------------------------------------------+
    | LONG           | %l                      | 25l                                                        |
    +----------------+-------------------------+------------------------------------------------------------+
    | DATE           | %d                      | 2022.01.01                                                 |
    +----------------+-------------------------+------------------------------------------------------------+
    | MONTH          | %M                      | 2022.05M                                                   |
    +----------------+-------------------------+------------------------------------------------------------+
    | TIME           | %t                      | 13:00:10.706                                               |
    +----------------+-------------------------+------------------------------------------------------------+
    | MINUTE         | %m                      | 13:30m                                                     |
    +----------------+-------------------------+------------------------------------------------------------+
    | SECOND         | %s                      | 13:30:10                                                   |
    +----------------+-------------------------+------------------------------------------------------------+
    | DATETIME       | %D                      | 2012.06.13 13:30:10                                        |
    |                |                         | 2012.06.13T13:30:10                                        |
    +----------------+-------------------------+------------------------------------------------------------+
    | TIMESTAMP      | %T                      | 2012.06.13 13:30:10.008                                    |
    |                |                         | 2012.06.13T13:30:10.008                                    |
    +----------------+-------------------------+------------------------------------------------------------+
    | NANOTIME       | %n                      | 13:30:10.008007006                                         |
    +----------------+-------------------------+------------------------------------------------------------+
    | NANOTIMESTAMP  | %N                      | 2012.06.13 13:30:10.008007006                              |
    |                |                         | 2012.06.13T13:30:10.008007006                              |
    +----------------+-------------------------+------------------------------------------------------------+
    | FLOAT          | %f                      | 2.1f                                                       |
    +----------------+-------------------------+------------------------------------------------------------+
    | DOUBLE         | %F                      | 2.1                                                        |
    +----------------+-------------------------+------------------------------------------------------------+
    | SYMBOL         | %S                      | symbol(["aaa", "bbb"])                                     |
    +----------------+-------------------------+------------------------------------------------------------+
    | STRING         | %W                      | "Hello"                                                    |
    +----------------+-------------------------+------------------------------------------------------------+
    | ANY (tuple)    | %A                      | (1, 45, 'sah')                                             |
    +----------------+-------------------------+------------------------------------------------------------+

    .. note::

        If the string contains a "%" character, it must be escaped by using a
        double percent sign (%%).

    You can specify formatting options inside the placeholders like `%[(var)][#][±][0][m/*][.][n/*]type`.

    Table 2. The following table lists the options which can be inserted before
    the decimal point `.` in placeholders:

    +-------------+------------------------------------------------------------+--------------------------------------------------------------------------------------+
    | Specifier   | Meaning                                                    | Examples                                                                             |
    +=============+============================================================+======================================================================================+
    | m (a        | [Used with %f, %F or %W]                                   | `stringFormat("%10f", pi)`                                                           |
    | positive    |                                                            | output: `··3.141593`                                                                 |
    | integer)    | For FLOAT (f) and DOUBLE (F) data types, m indicates the   |                                                                                      |
    |             | minimum total width of the output string.                  | `stringFormat("%2f", 12345.0)`                                                       |
    |             |                                                            | output: `12345.000000`                                                               |
    |             | If m is smaller than the actual total number of digits in  |                                                                                      |
    |             | the float number, the full float number is output directly | `stringFormat("%10W", "6chars")`                                                     |
    |             | (rounded to 6 decimal places if needed).                   | output: `····6chars`                                                                 |
    |             |                                                            |                                                                                      |
    |             | If m is greater than the total digits, the output string   |                                                                                      |
    |             | is padded with leading spaces by default.                  |                                                                                      |
    |             |                                                            |                                                                                      |
    |             | For STRING (W) data type, m indicates the minimum total    |                                                                                      |
    |             | length of the output string.                               |                                                                                      |
    |             |                                                            |                                                                                      |
    |             | If m is smaller than the actual string length, the full    |                                                                                      |
    |             | string is output.                                          |                                                                                      |
    |             |                                                            |                                                                                      |
    |             | If m is greater than the string length, the output string  |                                                                                      |
    |             | is padded with leading spaces. The output string is        |                                                                                      |
    |             | right-alignment by default.                                |                                                                                      |
    +-------------+------------------------------------------------------------+--------------------------------------------------------------------------------------+
    | \*          | Like m, \* indicates the minimum total width of the output | `stringFormat("%*f", (10,pi))`                                                       |
    |             | string. However, \* allows passing the width as an argument| output: `··3.141593`                                                                 |
    |             | (args). Specify the width in the corresponding argument    |                                                                                      |
    |             | (args) in tuple format: (width,value).                     |                                                                                      |
    +-------------+------------------------------------------------------------+--------------------------------------------------------------------------------------+
    | 0           | 0 pads numeric values with zeros. For left-aligned fields, | `stringFormat("%010f", pi)`                                                          |
    |             | the zeros are padded on the right side. If 0 is not        | output: `003.141593`                                                                 |
    |             | specified, the output string is padded with spaces.        |                                                                                      |
    +-------------+------------------------------------------------------------+--------------------------------------------------------------------------------------+
    | \-          | \- left-aligns the output string within the specified field| `stringFormat("%-10.3f", pi)`                                                        |
    |             | width.                                                     | output: `3.142`                                                                      |
    +-------------+------------------------------------------------------------+--------------------------------------------------------------------------------------+
    | \+          | \+ adds a plus sign "+" before positive values.            | `stringFormat("%+f", pi)`                                                            |
    |             |                                                            | output: `+3.141593`                                                                  |
    +-------------+------------------------------------------------------------+--------------------------------------------------------------------------------------+
    | (var)       | [Cannot be used with other specifiers]                     | `employee = {"name":"Lisa Mill", "year":2010}`                                       |
    |             |                                                            | `stringFormat("%(name)W joined the company in %(year)i", employee)`                  |
    |             | (var) allows you to format a string using a dictionary,    | output: `Lisa Mill joined the company in 2010`                                       |
    |             | where the dictionary keys act as variables in the string.  |                                                                                      |
    |             | To specify a key, put it in parentheses after the %        |                                                                                      |
    |             | symbol. The values in the dictionary are substituted into  |                                                                                      |
    |             | the string where the %(key)type placeholders are located.  |                                                                                      |
    +-------------+------------------------------------------------------------+--------------------------------------------------------------------------------------+
    | #           | [Used with %o, %x or %X]                                   | `stringFormat("%#o", 33)`                                                            |
    |             |                                                            | output: `0o41`                                                                       |
    |             | # adds "0o" before octal values; adds "0x" (lower case) or |                                                                                      |
    |             | "0X" (upper case) before hexadecimal values.               | `stringFormat("%#X", 33)`                                                            |
    |             |                                                            | output: `0X21`                                                                       |
    +-------------+------------------------------------------------------------+--------------------------------------------------------------------------------------+

    Table 3. The following table lists the options which can be inserted after
    the decimal point `.` in placeholders (these options can only be used with %f, %F or %W):

    +-------------------+-----------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------+
    | Specifier         | Meaning                                                                                                                           | Examples                                                                          |
    +===================+===================================================================================================================================+===================================================================================+
    | n (a positive     | For FLOAT (f) and DOUBLE (F) data types, n specifies the number of digits after the decimal point.                                | `stringFormat("%10.5f", pi)`                                                      |
    | integer)          |                                                                                                                                   | output: `···3.14159`                                                              |
    |                   | If n is smaller than the number of decimal digits, the float number is rounded to n digits.                                       |                                                                                   |
    |                   |                                                                                                                                   | `stringFormat('%10.3f' , 3.1)`                                                    |
    |                   | If n is greater than the number of decimal digits, zeros are padded to the right.                                                 | output: `·····3.100`                                                              |
    |                   |                                                                                                                                   |                                                                                   |
    |                   | For STRING (W) data type, n specifies the string length.                                                                          | `stringFormat("%2.10W", "6chars")`                                                |
    |                   |                                                                                                                                   | output: `6chars`                                                                  |
    |                   | If n is smaller than the actual length of string, the string is truncated to n characters.                                        |                                                                                   |
    |                   |                                                                                                                                   |                                                                                   |
    |                   | If n is greater than the actual length of string, the full string is output without padding.                                      |                                                                                   |
    +-------------------+-----------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------+
    | \*                | Like n, * specifies the number of digits after the decimal point. However, * allows specifying the number of decimals (precision) | Specify precision: `stringFormat("%.*f", (5,pi))`                                 |
    |                   | by passing it as an argument (args). Specify the digits in the corresponding argument in tuple format: ([width],[precision],value)| output: `3.14159`                                                                 |
    |                   |                                                                                                                                   |                                                                                   |
    |                   |                                                                                                                                   | Specify both the minimum field width and the precision:                           |
    |                   |                                                                                                                                   | `stringFormat("%0*.*f", (10,5,pi))`                                               |
    |                   |                                                                                                                                   | output: `···3.14159`                                                              |
    +-------------------+-----------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------+

    Parameters
    ----------
    format : Constant
        A string containing zero or more placeholders.
    """
    ...


@builtin_function(_strip)
def strip(X: Constant) -> Constant:
    r"""Remove all space, tab, new line, and carriage characters in both head and
    tail of a string.

    Parameters
    ----------
    X : Constant
        A literal scalar/vector.
    """
    ...


@builtin_function(_strlen)
def strlen(X: Constant) -> Constant:
    r"""Return the length of each string in X.

    Parameters
    ----------
    X : Constant
        A string scalar/vector.
    """
    ...


@builtin_function(_strlenu)
def strlenu(X: Constant) -> Constant:
    r"""Return the length of each string in X.

    Parameters
    ----------
    X : Constant
        A string scalar/vector.
    """
    ...


@builtin_function(_strpos)
def strpos(X: Constant, str: Constant) -> Constant:
    r"""If X contains str, return the index in X where the first occurrence of
    str starts; otherwise, return -1.

    Parameters
    ----------
    X : Constant
        A string scalar/vector.
    str : Constant
        A string scalar.
    """
    ...


@builtin_function(_sub)
def sub(X: Constant, Y: Constant) -> Constant:
    r"""Return the result of element-by-element subtracting Y from X.
    If both X and Y are sets, sub returns a set by eliminating the common elements of X and Y from X.

    Parameters
    ----------
    X : Constant
        A scalar/pair/vector/matrix/set.
    Y : Constant
        A scalar/pair/vector/matrix/set.
    """
    ...


@builtin_function(_subarray)
def subarray(X: Constant, range: Constant) -> Constant:
    r"""When a subset of the elements of a vector are needed in calculation,
    if we use script such as close[10:].avg(), a new vector close[10:] is
    generated with replicated data from the original vector close before the
    calculation is conducted. This not only consumes more memory but also takes time.

    Function subarray generates a subarray of the original vector. It only records
    the pointer to the original vector together with the starting and ending positions
    of the subarray. As the system does not allocate a large block of memory to store
    the subarray, data replication does not occur. All read-only operations on vectors
    can be applied directly to a subarray.

    Parameters
    ----------
    X : Constant
        A vector/matrix.
    range : Constant
        A pair of integers indicating a range. The lower bound is inclusive and
        the upper bound is exclusive.
    """
    ...


@builtin_function(_substr)
def substr(str: Constant, offset: Constant, length: Constant = DFLT) -> Constant:
    r"""Return a substring of X with the specified starting position (offset) and length.
    The first character of X corresponds to position 0. If length exceeds the
    length of X, stop at the end of X.

    If length is not specified, return a substring of X from the specified
    starting position (offset) to the end of X.

    Parameters
    ----------
    str : Constant
        A string scalar/vector.
    offset : Constant
        A nonnegative integer.
    length : Constant, optional
        A positive integer, by default DFLT.
    """
    ...


@builtin_function(_substru)
def substru(str: Constant, offset: Constant, length: Constant = DFLT) -> Constant:
    r"""The only differerence between substru and substr is that substru can process Unicode strings.

    Return a substring of X with the specified starting position (offset) and length.
    The first character of X corresponds to position 0. If length exceeds the
    length of X, stop at the end of X.

    If length is not specified, return a substring of X from the specified
    starting position (offset) to the end of X.

    Parameters
    ----------
    str : Constant
        A string scalar/vector.
    offset : Constant
        A nonnegative integer.
    length : Constant, optional
        A positive integer, by default DFLT.
    """
    ...


@builtin_function(_subtuple)
def subtuple(X: Constant, range: Constant) -> Constant:
    r"""Create a read-only view of a subarray of each vector in X almost instantly.
    In contrast, it takes time to create a new tuple of vectors.

    Parameters
    ----------
    X : Constant
        A tuple of vectors with the same length.
    range : Constant
        A pair of integers indicating a range. The lower bound is inclusive and
        the upper bound is exclusive.
    """
    ...


@builtin_function(_sum)
def sum(X: Constant) -> Constant:
    r"""If X is a vector, return the sum of all the elements in X.

    If X is a matrix, calculate the sum of each column of X and return a vector.

    If X is a table, calculate the sum of each column of X and return a table.

    As with all aggregate functions, null values are not included in the calculation.

    If all elements of a calculation are null values, the result is NULL.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_sum2)
def sum2(X: Constant) -> Constant:
    r"""If X is a vector, return the sum of squares of all the elements in X.

    If X is a matrix, calculate the sum of squares for each column of X and return a vector.

    If X is a table, calculate the sum of squares for each column of X and return a table.

    As with all aggregate functions, null values are not included in the calculation.

    If all elements of a calculation are null values, the result is NULL.

    Please note that the data type of the result is always DOUBLE, even if the data type of X is INT or LONG.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_sum3)
def sum3(X: Constant) -> Constant:
    r"""If X is a vector, return the sum of cubes of all the elements in X.

    If X is a matrix, calculate the sum of cubes for each column of X and return a vector.

    If X is a table, calculate the sum of cubes for each column of X and return a table.

    As with all aggregate functions, null values are not included in the calculation.

    If all elements of a calculation are null values, the result is NULL.

    Please note that the data type of the result is always DOUBLE, even if the data type of X is INT or LONG.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_sum4)
def sum4(X: Constant) -> Constant:
    r"""If X is a vector, return the sum of the fourth powers of all the elements in X.

    If X is a matrix, calculate the sum of the fourth powers for each column of X and return a vector.

    If X is a table, calculate the sum of the fourth powers for each column of X and return a table.

    As with all aggregate functions, null values are not included in the calculation.

    If all elements of a calculation are null values, the result is NULL.

    Please note that the data type of the result is always DOUBLE, even if the data type of X is INT or LONG.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix/table.
    """
    ...


@builtin_function(_sumbars)
def sumbars(X: Constant, threshold: Constant) -> Constant:
    r"""For each element X i in X, calculate the cumulative sum of X i in the
    backward direction, i.e., (X i + X i-1 + X i-2 …), until the value is no smaller than Y.

    If the cumulative sum never exceeds Y, return 0.

    Parameters
    ----------
    X : Constant
        A vector/tuple/matrix/table whose elements must be non-negative numbers.
    threshold : Constant
        A scalar indicating the threshold.
    """
    ...


@builtin_function(_summary)
def summary(X: Constant, interpolation: Constant = DFLT, characteristic: Constant = DFLT, percentile: Constant = DFLT, precision: Constant = DFLT, partitionSampling: Constant = DFLT) -> Constant:
    r"""summary generates summary statistics for the input data. It returns an in-memory
    table containing the minimum, maximum, count, mean, standard deviation, and
    specified percentiles in ascending order.

    - If X is a table, summary only computes statistics for the numeric columns.

    - If X is a data source, it can only contain numeric columns, otherwise an error
      will occur during computation.

    Parameters
    ----------
    X : Constant
        An in-memory table, DFS table or data source generated from sqlDS.
        Note that data sources with SQL metacode containing table joins are currently not supported.
    interpolation : Constant, optional
        A string indicating the interpolation method for percentiles, by default DFLT.

        It can be "linear" (default), "nearest", "lower", "higher" and "midpoint".
    characteristic : Constant, optional
        A string scalar or vector indicating the characteristics to compute, by default DFLT.

        It can be "avg" and/or "std". Default is both characteristics.
    percentile : Constant, optional
    A DOUBLE vector of percentiles to compute. Each vector element falls
        between 0 ang 100, by default DFLT.
    precision : Constant, optional
        A DOUBLE scalar greater than 0, by default DFLT.
    partitionSampling : Constant, optional
        Can be a positive integer specifying the number of partitions to sample,
        or a float between (0, 1] specifying the sampling ratio, by default DFLT.

        If not specified, statistics are computed on all partitions. When specifying
        partitionSampling

        .. note::

            - For a partitioned table:

              - at least one partition will always be sampled. If the sampling ratio * total partitions < 1, one partition is sampled.

              - The sampling ratio is rounded down if the sampling ratio * total partitions is not an integer. E.g. if ratio=0.26 and total partitions is 10, 2 partitions are sampled.

              - If partitionSampling (integer) > total partitions, all partitions are used.

            - partitionSampling has no effect for non-partitioned tables.
    """
    ...


@builtin_function(_svd)
def svd(obj: Constant, fullMatrices: Constant = DFLT, computeUV: Constant = DFLT) -> Constant:
    r"""Perform the singular decomposition of a matrix.

    Given an m-by-n matrix A:

    - If fullMatrices=true, return an m-by-m matrix U (unitary matrix having left
      singular vectors as columns), an n-by-n matrix V (unitary matrix having right
      singular vectors as rows) and a vector s (singular values sorted in descending
      order) such that A=U*S*V. S is an m-by-n matrix with s as the diagonal elements.

    - If fullMatrices=false, remove the extra rows or columns of zeros from matrix S,
      along with the columns/rows in U and V that multiply those zeros in the
      expression A = U*S*V. Removing these zeros and columns/rows can improve execution
      time and reduce storage requirements without compromising the accuracy of the
      decomposition. The resulting matrix U is m-by-k, matrix V is k-by-n and
      matrix S is k-by-k with k=min(m,n).

    - If computeUV=false, only return vector s.

    Parameters
    ----------
    obj : Constant
        A matrix.
    fullMatrices : Constant, optional
        A Boolean value, by default DFLT.
    computeUV : Constant, optional
        A Boolean value, by default DFLT.
    """
    ...


@builtin_function(_symbol)
def symbol(X: Constant) -> Constant:
    r"""Convert X to a symbol vector.

    Parameters
    ----------
    X : Constant
        A string/symbol vector.

    Returns
    -------
    Constant
        A symbol vector.
    """
    ...


@builtin_function(_symbolCode)
def symbolCode(X: Constant) -> Constant:
    r"""SYMBOL is a special STRING type used to store repetitive strings in DolphinDB.
    Internally, data of SYMBOL type is encoded into integers and stored as a dictionary.
    The internal encoding of an empty string is 0.

    For each element in X, this function returns its internal encoding. The return
    value is of the same dimension as X.

    It is recommended to use the SYMBOL type if there are a lot of duplicate values
    for a certain field such as device ID and stock symbol to improve storage efficiency.

    Parameters
    ----------
    X : Constant
        A vector/matrix of SYMBOL type.
    """
    ...


@builtin_function(_symmetricDifference)
def symmetricDifference(X: Constant, Y: Constant) -> Constant:
    r"""Return the union of two sets minus the intersection of the two sets.

    Parameters
    ----------
    X : Constant
        A set
    Y : Constant
        A set
    """
    ...


@builtin_function(_syncDict)
def syncDict(keyType: Union[Alias[Literal["keyObj"]], Constant], valueType: Union[Alias[Literal["valueObj"]], Constant], sharedName: Constant = DFLT, ordered: Constant = DFLT) -> Constant:
    r"""Return a thread-safe dictionary that allows concurrent read and write by multiple threads.

    Parameters
    ----------
    keyType : Union[Alias[Literal[&quot;keyObj&quot;]], Constant]
        The data type of dictionary keys. The following data categories are supported:
        Integral (excluding COMPRESSED), Temporal, Floating and Literal.
    valueType : Union[Alias[Literal[&quot;valueObj&quot;]], Constant]
        The data type of dictionary values. Note that COMPLEX/POINT is not supported.
    sharedName : Constant, optional
        A a string, by default DFLT. If it is specified, the dictionary is shared across sessions.
    ordered : Constant, optional
        A Boolean value, by default DFLT. The default value is false, which indicates
        to create a regular dictionary. True means to create an ordered dictionary.
        The regular dictionaries do not track the insertion order of the key-value p
        airs whereas the ordered dictionaries preserve the insertion order of key-value pairs.
    """
    ...


@builtin_function(_syntax)
def syntax(func: Constant) -> Constant:
    r"""Return the syntax of function/command X.

    Parameters
    ----------
    func : Constant
        A DolphinDB function/command.
    """
    ...


@builtin_function(_t3)
def t3(X: Constant, window: Constant, vfactor: Constant = DFLT) -> Constant:
    r"""Calculate the Triple Exponential Moving Average (t3) for X in a sliding window of the given length.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    window : Constant
        A positive integer indicating the size of the sliding window.
    vfactor : Constant, optional
        A floating-point number in [0,1]. The default value is 1.0, by default DFLT.
    """
    ...


@builtin_function(_tTest)
def tTest(X: Constant, Y: Constant = DFLT, mu: Constant = DFLT, confLevel: Constant = DFLT, equalVar: Constant = DFLT) -> Constant:
    r"""If Y is not specified, conduct a one-sample t-test on X. If Y is specified,
    conduct a paired-sample t-test on X and Y.

    Parameters
    ----------
    X : Constant
        A numeric vector indicating the sample for the t-test.
    Y : Constant, optional
        A numeric vector indicating the second sample for a paired-sample t-test, by default DFLT
    mu : Constant, optional
        A floating number, by default DFLT.  If Y is not specified, mu is the mean v
        alue of X in the null hypothesis; if Y is specified, mu is the difference
        in the mean values of X and Y in the null hypothesis.
    confLevel : Constant, optional
        A floating number between 0 and 1 indicating the confidence level of the test,
        by default DFLT
    equalVar : Constant, optional
        A Boolean value indicating whether the variance of X and Y are the same
        in the null hypothesis, by default DFLT.

    Returns
    -------
    Constant
        Return a dictionary with the following keys:

        - stat: a table with p-value and confidence interval under 3 alternative hypotheses.

        - df: degree of freedom

        - confLevel: confidence level

        - method: type of t-test used

        - tValue: t-stat
    """
    ...


@builtin_function(_table)
def table(*args) -> Constant:
    r"""- For `table(X, [X1], [X2], ...)`: Converts vectors/matrices/tuples, or the combination of vectors and tuples into a table.

    - For `table(capacity:size, colNames, colTypes)`: Creates an empty or initialized table of fixed data types.

    Returns
    -------
    Constant
        A table.
    """
    ...


@builtin_function(_tableInsert)
def tableInsert(table: Constant, *args) -> Constant:
    r"""Insert args... into table. Return the number of rows inserted from the operation.

    If args... is a table, it must have the same schema as table. If table is a
    partitioned table, args... must be a table.

    If args... is a tuple, it must have the same number of elements as the number
    of columns of table and each element of args... must have the same data type
    as the corresponding column of table.

    If args... is multiple vectors or tuples, the number of its elements must be
    the same as the number of columns of table and each vector or tuple must have
    the same data type as the corresponding column of table.

    If args... is a dictionary, its keys correspond to the column names of table.
    The values of args... must be a tuple. For this scenario table must be an in-memory table.

    Parameters
    ----------
    table : Constant
        A table object or a table name. The table can be either an in-memory table
        or a DFS table. In remote call, it must be a table name as we don't have
        the reference of a table object.

    Returns
    -------
    Constant
        An integer indicating the number of rows inserted from the operation.
    """
    ...


@builtin_function(_tableUpsert)
def tableUpsert(obj: Constant, newData: Constant, ignoreNull: Constant = DFLT, keyColNames: Constant = DFLT, sortColumns: Constant = DFLT) -> Constant:
    r"""Insert rows into a table if the values with the key do not already exist,
    or update them if they do.

    Parameters
    ----------
    obj : Constant
        A keyed table, indexed table, or a DFS table.
    newData : Constant
        An in-memory table.
    ignoreNull : Constant, optional
        A Boolean value, by default DFLT.  If set to true, for the null values in
        newData, the corresponding elements in obj are not updated.
    keyColNames : Constant, optional
        A STRING scalar/vector, by default DFLT. When obj is a DFS table,
        keyColNames are considered as the key columns.
    sortColumns : Constant, optional
        A STRING scalar or vector, by default DFLT. The updated partitions will
        be sorted on sortColumns (only within each partition, not across partitions).

        .. note::

            - sortColumns is supported in upser_ only with the OLAP engine.

            - To specify sortColumns, obj must be a DFS table.

            - When obj is an empty table, setting sortColumns has no effect. That is, the system will not sort the inserted data.

    Returns
    -------
    Constant
        A LONG pair. The first element represents the number of inserted records,
        and the second represents the number of updated records.
    """
    ...


@builtin_function(_tail)
def tail(obj: Constant, n: Constant = DFLT) -> Constant:
    r"""Return the last n element(s) of a vector, or the last n columns of a matrix,
    or the last n rows of a table.

    Parameters
    ----------
    obj : Constant
        A vector/matrix/table.
    n : Constant, optional
        A positive integer, by default DFLT
    """
    ...


@builtin_function(_take)
def take(X: Constant, n: Constant) -> Constant:
    r"""- If X is a scalar (n must also be a scalar): Generates a vector containing n identical values of X.

    - If X is a vector or a tuple:

      - if n is a scalar: takes n elements from X sequentially. It can be left to right (if n > 0) or right to left (if n < 0). The result is a vector.

      - if n is a vector (must be of the same length as X): takes n[i] copies of X[i]. If n[i] <= 0, it skips X[i]. The result is a vector.

    - If X is a matrix or table:

      - if n is a scalar: It takes n rows of X sequentially, either from top to bottom (if n > 0) or bottom to top (if n < 0). The result is a matrix or table.

      - if n is a vector (must be of the same length as the number of rows in X): takes n[i] copies of the element at the i-th row of X. If n[i] <= 0, it skips the i-th row and takes no elements. The result is a matrix or table.

    Parameters
    ----------
    X : Constant
        A scalar/vector/tuple/matrix/table.
    n : Constant
        An integer or a vector of integers.
    """
    ...


@builtin_function(_talib)
def talib(func: Constant, *args) -> Constant:
    r"""Regarding null value handling, the differences between DolphinDB's built-in
    moving functions and Python TA-lib lie in:

    - DolphinDB moving functions: The calculation in the sliding window starts from the first element.

    - Python TA-lib: Keep the null values at the beginning of data in the output. The calculation in the sliding window starts from the first non-null value.

    Parameters
    ----------
    func : Constant
        A function.
    """
    ...


@builtin_function(_talibNull)
def talibNull(*args) -> Constant:
    r"""Traverse each vector (v1, v2, …, vn) based on the index starting from 0 and return a tuple.

    If all values at index i (v1[i], v2[i], ..., vn[i] ) are non-null values,
    then the elements at index 0 to index i take the null values, and values of
    the element after index i remain unchanged.
    """
    ...


@builtin_function(_tan)
def tan(X: Constant) -> Constant:
    r"""The tangent function.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix.
    """
    ...


@builtin_function(_tanh)
def tanh(X: Constant) -> Constant:
    r"""The hyperbolic tangent function.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix.
    """
    ...


@builtin_function(_tanimoto)
def tanimoto(X: Constant, Y: Constant) -> Constant:
    r"""If X and Y are scalars or vectors, return the result of their tanimoto distance.

    If X or Y is a matrix, return a vector that is the result of the tanimoto distance
    between elements in each column. Note that if both X and Y are indexed matrices or
    indexed series, return the results of rows with the same label. Rows with different
    labels will be ignored.

    As with all other aggregate functions, null values are ignored in the calculation.

    Here is the formula of Tanimoto similarity (similar). Tanimoto distance is calculated as 1-similar.

    Parameters
    ----------
    X : Constant
        A numeric scalar, or vector/matrix.
    Y : Constant
        A numeric scalar, or vector/matrix.
    """
    ...


@builtin_function(_tema)
def tema(X: Constant, window: Constant) -> Constant:
    r"""Calculate the Triple Exponential Moving Average (tema) for X in a sliding
    window of the given length.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    window : Constant
        A positive integer indicating the size of the sliding window.
    """
    ...


@builtin_function(_temporalAdd)
def temporalAdd(obj: Constant, duration: Constant, unit: Constant = DFLT) -> Constant:
    r"""Add a value to a temporal variable.

    Parameters
    ----------
    obj : Constant
        A temporal scalar/pair/vector.
    duration : Constant
        An integer.
    unit : Constant, optional
        A STRING vector, by default DFLT.

        - When parameter duration is an integer, unit is:

          - the unit of parameter duration. It can be "ns"(nanosecond), "us"(microsecond),
            "ms"( millisecond), "s"(second), "m"(minute), "H"(hour), "d"(day), "w"(week),
            "M"(month), "y"( year), or "B"(business day).

          - the identifier of trading calendar, e.g., the Market Identifier Code
            of an exchange, or a user-defined calendar name. The corresponding
            file must be saved in marketHolidayDir.

        - When duration is of DURATION type, this parameter is not required.

        .. note::

            When unit is "y" or "M", the result is consistent with mysql. Pandas
            provides an offset object Dateoffsets to move dates forward a given
            number of valid dates. When the DateOffset parameter is specified as
            months or years, the result is also consistent with temporalAdd.
    """
    ...


@builtin_function(_temporalFormat)
def temporalFormat(X: Constant, format: Constant) -> Constant:
    r"""Convert a DolphinDB temporal variable to a string with specified format.
    For details about DolphinDB temporal formats, please check the section
    Parsing and Format of Temporal Variables.

    Parameters
    ----------
    X : Constant
        A scalar/vector of temporal data types.
    format : Constant
        A string indicating a temporal format.
    """
    ...


@builtin_function(_temporalParse)
def temporalParse(X: Constant, format: Constant) -> Constant:
    r"""Convert a string with specified format to a DolphinDB temporal data type.
    Return NULL if it cannot decide on the data type.

    DolphinDB has the following temporal formats:

    +-------------+---------------------+--------------------------------------------+
    | Format      | Meaning             | Range of value                             |
    +=============+=====================+============================================+
    | yyyy        | year (4 digits)     | 1000-9999                                  |
    +-------------+---------------------+--------------------------------------------+
    | yy          | year (2 digits)     | 00-99. (00-39: 2000-2039; 40-99: 1940-1999)|
    +-------------+---------------------+--------------------------------------------+
    | MM          | month in year       | 1-12                                       |
    +-------------+---------------------+--------------------------------------------+
    | MMM         | month in year       | JAN, FEB, ... DEC (case insensitive)       |
    +-------------+---------------------+--------------------------------------------+
    | dd          | day in month        | 1-31                                       |
    +-------------+---------------------+--------------------------------------------+
    | HH          | hour in day         | 0-23                                       |
    +-------------+---------------------+--------------------------------------------+
    | hh          | hour in AM/PM       | 0-11                                       |
    +-------------+---------------------+--------------------------------------------+
    | mm          | minute in hour      | 0-59                                       |
    +-------------+---------------------+--------------------------------------------+
    | ss          | second in minute    | 0-59                                       |
    +-------------+---------------------+--------------------------------------------+
    | aa          | AM/PM marker        | AM, PM. (case-insensitive)                 |
    +-------------+---------------------+--------------------------------------------+
    | SSS         | millisecond         | 0-999                                      |
    +-------------+---------------------+--------------------------------------------+
    | nnnnnn      | microsecond         | 0-999999                                   |
    +-------------+---------------------+--------------------------------------------+
    | nnnnnnnnn   | nanosecond          | 0-999999999                                |
    +-------------+---------------------+--------------------------------------------+

    Parameters
    ----------
    X : Constant
        A string scalar/vector to be converted to temporal data types.
    format : Constant
        A string indicating a temporal format.
    """
    ...


@builtin_function(_temporalSeq)
def temporalSeq(start: Constant, end: Constant, rule: Constant, closed: Constant = DFLT, label: Constant = DFLT, origin: Constant = DFLT) -> Constant:
    r"""Resample the time series between start and end based on the frequency specified by rule.

    Parameters
    ----------
    start : Constant
        A temporal scalar.
    end : Constant
        A temporal scalar. Its data type must be the same as start, and its
        value must be greater than start.
    rule : Constant
        A string that can take the following values:

        +---------------+----------------------+
        | Values of rule| DolphinDB function   |
        +===============+======================+
        | "B"           | businessDay          |
        +---------------+----------------------+
        | "W"           | weekEnd              |
        +---------------+----------------------+
        | "WOM"         | weekOfMonth          |
        +---------------+----------------------+
        | "LWOM"        | lastWeekOfMonth      |
        +---------------+----------------------+
        | "M"           | monthEnd             |
        +---------------+----------------------+
        | "MS"          | monthBegin           |
        +---------------+----------------------+
        | "BM"          | businessMonthEnd     |
        +---------------+----------------------+
        | "BMS"         | businessMonthBegin   |
        +---------------+----------------------+
        | "SM"          | semiMonthEnd         |
        +---------------+----------------------+
        | "SMS"         | semiMonthBegin       |
        +---------------+----------------------+
        | "Q"           | quarterEnd           |
        +---------------+----------------------+
        | "QS"          | quarterBegin         |
        +---------------+----------------------+
        | "BQ"          | businessQuarterEnd   |
        +---------------+----------------------+
        | "BQS"         | businessQuarterBegin |
        +---------------+----------------------+
        | "REQ"         | fy5253Quarter        |
        +---------------+----------------------+
        | "A"           | yearEnd              |
        +---------------+----------------------+
        | "AS"          | yearBegin            |
        +---------------+----------------------+
        | "BA"          | businessYearEnd      |
        +---------------+----------------------+
        | "BAS"         | businessYearBegin    |
        +---------------+----------------------+
        | "RE"          | fy5253               |
        +---------------+----------------------+
        | "D"           | date                 |
        +---------------+----------------------+
        | "H"           | hourOfDay            |
        +---------------+----------------------+
        | "U"           | microsecond          |
        +---------------+----------------------+
        | "L"           | millisecond          |
        +---------------+----------------------+
        | "min"         | minuteOfHour         |
        +---------------+----------------------+
        | "N"           | nanosecond           |
        +---------------+----------------------+
        | "S"           | secondOfMinute       |
        +---------------+----------------------+
        | "SA"          | semiannualEnd        |
        +---------------+----------------------+
        | "SAS"         | semiannualBegin      |
        +---------------+----------------------+

        The strings above can also be used with integers for parameter "rule".
        For example, "2M" means the end of every two months. In addition, rule
        can also be set as the identifier of the trading calendar, e.g., the Market
        Identifier Code of an exchange, or a user-defined calendar name.

    closed : Constant, optional
        A a string indicating which boundary of the interval is closed, by default DFLT.

        - The default value is 'left' for all values of rule except for 'M', 'A',
          'Q', 'BM', 'BA', 'BQ', and 'W' which all have a default of 'right'.

        - The default is 'right' if origin is 'end' or 'end_day'.

    label : Constant, optional
        A string indicating which boundary is used to label the interval, by default DFLT.

        - The default value is 'left' for all values of rule except for 'M', 'A',
          'Q', 'BM', 'BA', 'BQ', and 'W' which all have a default of 'right'.

        - The default is 'right' if origin is 'end' or 'end_day'.
    origin : Constant, optional
        A string or a scalar of the same data type as X, indicating the timestamp
        where the intervals start, by default DFLT. It can be 'epoch', start',
        'start_day', 'end', 'end_day' or a user-defined time object.

        - 'epoch': origin is 1970-01-01

        - 'start': origin is the first value of the timeseries

        - 'start_day': origin is 00:00 of the first day of the timeseries

        - 'end': origin is the last value of the timeseries

        - 'end_day': origin is 24:00 of the last day of the timeseries
    """
    ...


@builtin_function(_tensor)
def tensor(X: Constant) -> Constant:
    r"""Generate a tensor from X with the following rules:

    +--------------------------------------------+-------------------------------+
    | X                                          | Output                        |
    +============================================+===============================+
    | scalar                                     | 1D tensor                     |
    +--------------------------------------------+-------------------------------+
    | vector                                     | 1D tensor                     |
    +--------------------------------------------+-------------------------------+
    | columnar tuple                             | 2D tensor                     |
    +--------------------------------------------+-------------------------------+
    | matrix                                     | 2D tensor                     |
    +--------------------------------------------+-------------------------------+
    | table (with all columns of the same type)  | 2D tensor                     |
    +--------------------------------------------+-------------------------------+
    | tuple of vectors (each element is a        | 2D tensor                     |
    | vector of the same type)                   |                               |
    +--------------------------------------------+-------------------------------+
    | tuple of matrices (each element is a       | 3D tensor                     |
    | matrix with the same dimensions and type)  |                               |
    +--------------------------------------------+-------------------------------+
    | tuple of tuples (each element is a tuple,  | 3D tensor                     |
    | and each element of the sub-tuples is a    |                               |
    | vector of the same type)                   |                               |
    +--------------------------------------------+-------------------------------+
    | n-level nested tuple                       | n-D tensor (where n <= 10)    |
    +--------------------------------------------+-------------------------------+

    .. note::

        Tensors are mainly used with the DolphinDB plugins (such as LibTorch) for
        data exchange with deep learning frameworks. DolphinDB does not currently
        support direct storage and computation of tensors, nor direct access or
        modification to their elements.

    Parameters
    ----------
    X : Constant
        A scalar, vector, tuple, columnar tuple, matrix or table. These data types
        are supported: BOOL, CHAR, SHORT, INT, LONG, FLOAT, DOUBLE
    """
    ...


@builtin_function(_textChunkDS)
def textChunkDS(filename: Constant, chunkSize: Constant, delimiter: Constant = DFLT, schema: Constant = DFLT, skipRows: Constant = DFLT, arrayDelimiter: Constant = DFLT, containHeader: Constant = DFLT, arrayMarker: Constant = DFLT) -> Constant:
    r"""To load an extremely large text file into DolphinDB database, we can first
    use function textChunkDS to divide the text file into multiple data sources
    with the size of each data source specified by chunkSize, then use function
    mr to load data.

    When loading data files in DolphinDB, a random sample of the data is analyzed to
    determine the data type for each column. However, this sampling method does not
    always accurately determine the column types. It is recommend to use the extractTextSchema
    function to check the schema of the input file before loading the data. You can specify
    the intended data type for each column in the "type" field of the schema. For date or
    time columns particularly, if DolphinDB does not recognize the correct data types,
    you need to set the temporal type in the "type" field, and provide the date/time
    format string (e.g. "MM/dd/yyyy") in the "format" field. Refer to Parsing and
    Format of Temporal Variables for temproal formats in DolphinDB.

    Parameters
    ----------
    filename : Constant
        A string indicating the input text file name with its absolute path.
        Currently only .csv files are supported.
    chunkSize : Constant
        A positive integer indicating the size of a file chunk (in MB). The upper
        limit is max(maxMemSize / workerNum, 2048MB), representing the greater
        of the maximum available memory per worker or 2048MB.
    delimiter : Constant, optional
        A STRING scalar indicating the table column separator, by default DFLT.
        It can consist of one or more characters, with the default being a comma (',').
    schema : Constant, optional
        A table, by default DFLT. It can have the following columns, among which
        "name" and "type" columns are required.

        +--------+-----------------------+-----------------------------------+
        | Column | Data Type             | Description                       |
        +========+=======================+===================================+
        | name   | STRING scalar         | column name                       |
        +--------+-----------------------+-----------------------------------+
        | type   | STRING scalar         | data type                         |
        +--------+-----------------------+-----------------------------------+
        | format | STRING scalar         | the format of temporal columns    |
        +--------+-----------------------+-----------------------------------+
        | col    | INT scalar or vector  | the columns to be loaded          |
        +--------+-----------------------+-----------------------------------+

    skipRows : Constant, optional
        An integer between 0 and 1024 indicating the rows in the beginning of the
        text file to be ignored, by default DFLT.
    arrayDelimiter : Constant, optional
        A single character indicating the delimiter for columns holding the array
        vectors in the file, by default DFLT. Since the array vectors cannot be
        recognized automatically, you must use the schema parameter to update
        the data type of the type column with the corresponding array vector
        data type before import.
    containHeader : Constant, optional
        A Boolean value indicating whether the file contains a header row, by default DFLT.
        See loadText for the detailed determining rules.
    arrayMarker : Constant, optional
        A string containing 2 characters or a CHAR pair, by default DFLT. These two
        characters represent the identifiers for the left and right boundaries of an array vector.

        It cannot contain spaces, tabs (\\t), or newline characters (\\t or \\n).

        - It cannot contain digits or letters.

        - If one is a double quote ("), the other must also be a double quote.

        - If the identifier is ', ", or \\, a backslash ( \\ ) escape character should be used as appropriate. For example, arrayMarker="\\"\\"".

        - If delimiter specifies a single character, arrayMarker cannot contain the same character.

        - If delimiter specifies multiple characters, the left boundary of arrayMarker cannot be the same as the first character of delimiter.
    """
    ...


@builtin_function(_til)
def til(n: Constant) -> Constant:
    r"""Return a vector of integral type from 0 to n-1. If n=0, return an empty vector.

    The result is of the same data type as n. For example, if n is of LONG type,
    return a FAST LONG VECTOR.

    Parameters
    ----------
    n : Constant
        A non-negative integer.
    """
    ...


@builtin_function(_time)
def time(X: Constant) -> Constant:
    r"""Return the corresponding time(s) with millisecond precision. The data type of the result is TIME.

    Parameters
    ----------
    X : Constant
        A temporal scalar/vector.
    """
    ...


@builtin_function(_timestamp)
def timestamp(X: Constant) -> Constant:
    r"""Return the corresponding timestamp(s). The data type of the result is TIMESTAMP.

    Parameters
    ----------
    X : Constant
        A temporal scalar/vector.
    """
    ...


@builtin_function(_tmLowRange)
def tmLowRange(T: Constant, X: Constant, window: Constant) -> Constant:
    r"""For each element Xi in a sliding window of X, count the continuous nearest neighbors to its left that are larger than Xi. Null values are treated as the minimum values.

    If X is a matrix, conduct the aforementioned calculation within each column of X.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_tmTopRange)
def tmTopRange(T: Constant, X: Constant, window: Constant) -> Constant:
    r"""For each element Xi in a sliding window of X, count the continuous nearest
    neighbors to its left that are smaller than Xi. Null values are treated as the minimum values.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_tmavg)
def tmavg(T: Constant, X: Constant, window: Constant) -> Constant:
    r"""Calculate the moving average of X in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_tmbeta)
def tmbeta(T: Constant, Y: Constant, X: Constant, window: Constant) -> Constant:
    r"""Calculate the coefficient estimate of an ordinary-least-squares regression
    of Y on X in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    Y : Constant
        A vector of the same size as T.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_tmcorr)
def tmcorr(T: Constant, X: Constant, Y: Constant, window: Constant) -> Constant:
    r"""Calculate the correlation of X and Y in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    Y : Constant
        A vector of the same size as T.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_tmcount)
def tmcount(T: Constant, X: Constant, window: Constant) -> Constant:
    r"""Return the number of non-null values of X in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    Y : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_tmcovar)
def tmcovar(T: Constant, X: Constant, Y: Constant, window: Constant) -> Constant:
    r"""Calculate the moving covariance of X and Y in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    Y : Constant
        A vector of the same size as T.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_tmfirst)
def tmfirst(T: Constant, X: Constant, window: Constant) -> Constant:
    r"""Return the first element of X in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_tmkurtosis)
def tmkurtosis(T: Constant, X: Constant, window: Constant, biased: Constant = DFLT) -> Constant:
    r"""Calculate the moving kurtosis of X in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    biased : Constant, optional
        A Boolean value indicating whether the result is biased, by default DFLT.
    """
    ...


@builtin_function(_tmlast)
def tmlast(T: Constant, X: Constant, window: Constant) -> Constant:
    r"""Return the last element of X in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_tmmax)
def tmmax(T: Constant, X: Constant, window: Constant) -> Constant:
    r"""Calculate the moving maximum of X in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_tmmed)
def tmmed(T: Constant, X: Constant, window: Constant) -> Constant:
    r"""Calculate the moving median of X in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_tmmin)
def tmmin(T: Constant, X: Constant, window: Constant) -> Constant:
    r"""Calculate the moving minimum of X in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_tmove)
def tmove(T: Constant, X: Constant, window: Constant) -> Constant:
    r"""For each element T i in T, return the element in X which is at the same position
    as (T i-window) in T. If there is no match of (T i - window) in T, return the
    corresponding element in X at the previous adjacent time of (Ti - window).

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_tmoving)
def tmoving(func: Constant, T: Constant, funcArgs: Constant, window: Constant, excludedPeriod: Constant = DFLT) -> Constant:
    r"""Apply the function/operator to a sliding window of the given objects.

    The tmoving template always returns a vector with the same number of elements
    as the number of rows in the input arguments.

    Each of the built-in tm-functions such as tmsum, tmcount and tmavg is optimized
    for its specific use case. Therefore, they have much better performance than
    the tmoving template.

    Parameters
    ----------
    func : Constant
        A function.
    T : Constant
        A non-strictly increasing vector of temporal or integral type. It cannot contain null values.
    funcArgs : Constant
        The parameters of func. They can be vectors/dictionaries/tables.
        It is a tuple if there are more than one parameter of func,
        and all parameters must have the same size.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.

        For each element Ti in T:

        - When T is an integral value, the range of the corresponding window is (Ti - window, Ti]

        - When T is a temporal value, the range of the corresponding window is
          (temporalAdd(Ti, -window), Ti]
    excludedPeriod : Constant, optional
        A pair of time values (of TIME, NANOTIME, MINUTE, and SECOND type)
        representing the start and end time of the period which is excluded from
        the calculation, by default DFLT.

        When the excludedPeriod is set, the input T cannot contain the time range
        specified by excludedPeriod and must be of TIMESTAMP, NANOTIMESTAMP, TIME,
        and NANOTIME types. Note that excludedPeriod must be within a calendar day
        and cannot be longer than the value of (24 - window).
    """
    ...


@builtin_function(_tmpercentile)
def tmpercentile(T: Constant, X: Constant, percent: Constant, window: Constant, interpolation: Constant = DFLT) -> Constant:
    r"""Return the percentile rank of each element of X in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    percent : Constant
        An integer or floating number between 0 and 100.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    interpolation : Constant, optional
        A string indicating the interpolation method to use if the specified
        percentile is between two elements in X (assuming the :math:`i^{th}` and :math::math:`(i+1)^{th}`
        element in the sorted X) , by default DFLT. It can be 'linear', 'lower', 'higher',
        'nearest', and 'midpoint'.
    """
    ...


@builtin_function(_tmprod)
def tmprod(T: Constant, X: Constant, window: Constant) -> Constant:
    r"""Calculate the moving product of X in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_tmrank)
def tmrank(T: Constant, X: Constant, ascending: Constant, window: Constant, ignoreNA: Constant = DFLT, tiesMethod: Constant = DFLT, percent: Constant = DFLT) -> Constant:
    r"""Return the rank of each element of X in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    ascending : Constant
        A Boolean value. The default value is true indicating the sorting direction is ascending.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    ignoreNA : Constant, optional
        A Boolean value indicating whether null values are ignored in ranking, by default DFLT.
    tiesMethod : Constant, optional
        A string indicating how to rank the group of records with the same value
        (i.e., ties), by default DFLT.

        - "min": lowest rank of the group

        - "max": highest rank of the group

        - "average": average rank of the group

    percent : Constant, optional
        A Boolean value, indicating whether to display the returned rankings in
        percentile form, by default DFLT.
    """
    ...


@builtin_function(_tmskew)
def tmskew(T: Constant, X: Constant, window: Constant, biased: Constant = DFLT) -> Constant:
    r"""Calculate the moving skewness of X in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    biased : Constant, optional
        A Boolean value indicating whether the result is biased, by default DFLT.
    """
    ...


@builtin_function(_tmstd)
def tmstd(T: Constant, X: Constant, window: Constant) -> Constant:
    r"""Calculate the standard deviation of X in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_tmstdp)
def tmstdp(T: Constant, X: Constant, window: Constant) -> Constant:
    r"""Calculate the population standard deviation of X in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_tmsum)
def tmsum(T: Constant, X: Constant, window: Constant) -> Constant:
    r"""Calculate the moving sum of X in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_tmsum2)
def tmsum2(T: Constant, X: Constant, window: Constant) -> Constant:
    r"""Calculate the moving sum of squares of all elements of X in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.

    Returns
    -------
    Constant
        A vector of DOUBLE type.
    """
    ...


@builtin_function(_tmvar)
def tmvar(T: Constant, X: Constant, window: Constant) -> Constant:
    r"""Calculate the moving variance of X in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_tmvarp)
def tmvarp(T: Constant, X: Constant, window: Constant) -> Constant:
    r"""Calculate the moving population variance of X in a sliding window.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_tmwavg)
def tmwavg(T: Constant, X: Constant, Y: Constant, window: Constant) -> Constant:
    r"""Calculate the moving average of X with Y as weights in a sliding window.

    The weights in a sliding window are automatically adjusted so that the sum of weights for all non-Null elements in the sliding window is 1.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    Y : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_tmwsum)
def tmwsum(T: Constant, X: Constant, Y: Constant, window: Constant) -> Constant:
    r"""Calculate the moving sum of X with Y as weights in a sliding window.

    The weights in a sliding window are automatically adjusted so that the sum of weights for all non-null elements in the sliding window is 1.

    Parameters
    ----------
    T : Constant
        A non-strictly increasing vector of temporal or integral type.
        It cannot contain null values.
    X : Constant
        A vector of the same size as T.
    Y : Constant
        A vector of the same size as T.
    window : Constant
        A scalar of positive integer or DURATION type indicating the size of the sliding window.
    """
    ...


@builtin_function(_toCharArray)
def toCharArray(X: Constant) -> Constant:
    r"""Split a string into a vector of the CHAR data type.

    - If X is a scalar, return a vector.

    - If X is a vector, return an array vector.

    Parameters
    ----------
    X : Constant
        A scalar/vector of the STRING/BLOB/SYMBOL data type.
    """
    ...


@builtin_function(_toJson)
def toJson(obj: Constant) -> Constant:
    r"""Convert a DolphinDB object to JSON format. The result includes
    5 key-value pairs: name, form, type, size and value.

    For different data forms, the maximum length of the data to be converted differs:

    +------------+-----------+
    | Data Forms | Max Length|
    +============+===========+
    | matrix     | 300000    |
    +------------+-----------+
    | set        | 300000    |
    +------------+-----------+
    | vector     | 300000    |
    +------------+-----------+
    | dict       | 300000    |
    +------------+-----------+
    | table      | 100000    |
    +------------+-----------+

    Parameters
    ----------
    obj : Constant
        Can be any data type.
    """
    ...


@builtin_function(_toStdJson)
def toStdJson(obj: Constant) -> Constant:
    r"""Convert a DolphinDB object to JSON format.

    Parameters
    ----------
    obj : Constant
        Cannot be of data form matrix or pair, nor can it be of data type UUID,
        IPADDR, INT128, COMPRESSED, or system types.
    """
    ...


@builtin_function(_toUTF8)
def toUTF8(str: Constant, encode: Constant) -> Constant:
    r"""Change the encoding of strings to UTF-8.

    For the Windows version, encode can only be "gbk".

    Parameters
    ----------
    str : Constant
        A string scalar/vector.
    encode : Constant
        A string indicating the original encoding name. It must use lowercase.
    """
    ...


@builtin_function(_today)
def today() -> Constant:
    r"""Return the current date.

    Returns
    -------
    Constant
        A DATE scalar.
    """
    ...


@builtin_function(_topRange)
def topRange(X: Constant) -> Constant:
    r"""For each element Xi in X, count the continuous nearest neighbors to its
    left that are smaller than Xi.

    For each element in X, the function return the maximum length of a window to
    the left of X where it is the max/min. For example, after how many days a stock hits a new high.

    Parameters
    ----------
    X : Constant
        A vector/tuple/matrix/table.
    """
    ...


@builtin_function(_transDS_)
def transDS_(ds: Constant, transFunc: Constant) -> Constant:
    r"""Apply data transforming functions to a data source or a list of data sources.

    Parameters
    ----------
    ds : Constant
        A data source or a list of data sources. It is the sole argument of all
        the functions in transFunc.
    transFunc : Constant
        A function to be applied to ds.
    """
    ...


@builtin_function(_transFreq)
def transFreq(X: Constant, rule: Constant, closed: Constant = DFLT, label: Constant = DFLT, origin: Constant = DFLT) -> Constant:
    r"""For each element of X, conduct a transformation as specified with parameter rule.
    The result has the same length as X.

    Parameters
    ----------
    X : Constant
        A scalar/vector of temporal type.
    rule : Constant
        A string that can take the following values:

        +----------------------------+---------------------------+
        | Values of parameter "rule" | Corresponding DolphinDB   |
        |                            | function                  |
        +============================+===========================+
        | B                          | businessDay               |
        +----------------------------+---------------------------+
        | W                          | weekEnd                   |
        +----------------------------+---------------------------+
        | WOM                        | weekOfMonth               |
        +----------------------------+---------------------------+
        | LWOM                       | lastWeekOfMonth           |
        +----------------------------+---------------------------+
        | M                          | monthEnd                  |
        +----------------------------+---------------------------+
        | MS                         | monthBegin                |
        +----------------------------+---------------------------+
        | BM                         | businessMonthEnd          |
        +----------------------------+---------------------------+
        | BMS                        | businessMonthBegin        |
        +----------------------------+---------------------------+
        | SM                         | semiMonthEnd              |
        +----------------------------+---------------------------+
        | SMS                        | semiMonthBegin            |
        +----------------------------+---------------------------+
        | Q                          | quarterEnd                |
        +----------------------------+---------------------------+
        | QS                         | quarterBegin              |
        +----------------------------+---------------------------+
        | BQ                         | businessQuarterEnd        |
        +----------------------------+---------------------------+
        | BQS                        | businessQuarterBegin      |
        +----------------------------+---------------------------+
        | A                          | yearEnd                   |
        +----------------------------+---------------------------+
        | AS                         | yearBegin                 |
        +----------------------------+---------------------------+
        | BA                         | businessYearEnd           |
        +----------------------------+---------------------------+
        | BAS                        | businessYearBegin         |
        +----------------------------+---------------------------+
        | D                          | date                      |
        +----------------------------+---------------------------+
        | H                          | hourOfDay                 |
        +----------------------------+---------------------------+
        | min                        | minuteOfHour              |
        +----------------------------+---------------------------+
        | S                          | secondOfMinute            |
        +----------------------------+---------------------------+
        | L                          | millisecond               |
        +----------------------------+---------------------------+
        | U                          | microsecond               |
        +----------------------------+---------------------------+
        | N                          | nanosecond                |
        +----------------------------+---------------------------+
        | SA                         | semiannualEnd             |
        +----------------------------+---------------------------+
        | SAS                        | semiannualBegin           |
        +----------------------------+---------------------------+

        The strings above can also be used with positive integers for parameter rule.
        For example, "2M" means the end of every two months. In addition, rule
        can also be set as the identifier of the trading calendar, e.g., the
        Market Identifier Code of an exchange, or a user-defined calendar name.
        Positive integers can also be used with identifiers. For example, "2XNYS"
        means every two trading days of New York Stock Exchange.

    closed : Constant, optional
        A string indicating which boundary of the interval is closed, by default DFLT.

        - The default value is 'left' for all values of rule except for 'M', 'A',
          'Q', 'BM', 'BA', 'BQ', and 'W' which all have a default of 'right'.

        - The default is 'right' if origin is 'end' or 'end_day'.
    label : Constant, optional
        A string indicating which boundary is used to label the interval, by default DFLT.

        - The default value is 'left' for all values of rule except for 'M', 'A',
          'Q', 'BM', 'BA', 'BQ', and 'W' which all have a default of 'right'.

        - The default is 'right' if origin is 'end' or 'end_day'.
    origin : Constant, optional
        A string or a scalar of the same data type as X, indicating the timestamp
        where the intervals start. It can be 'epoch', start', 'start_day', 'end',
        'end_day' or a user-defined time object, by default DFLT.

        - 'epoch': origin is 1970-01-01

        - 'start': origin is the first value of the timeseries

        - 'start_day': origin is 00:00 of the first day of the timeseries

        - 'end': origin is the last value of the timeseries

        - 'end_day': origin is 24:00 of the last day of the timeseries
    """
    ...


@builtin_function(_transpose)
def transpose(obj: Constant) -> Constant:
    r"""This function is used to transpose X:

    - If X is a tuple: return a tuple of the same length as each element of X. The n-th element of the result is a vector composed of the n-th element of each element of X.

    - If X is a matrix: return the transpose of X.

    - If X is a table: convert X into an ordered dictionary. The dictionary keys are column names. Each dictionary value is a vector of the corresponding column.

    - If X is a dictionary: convert X into a table. The dictionary keys must be of STRING type:

      - When values are scalars or vectors of equal length, the keys of X serve as the column names and the cooresponding values populate the column values in the table.

      - When the values are dictionaries, the resulting table will have the keys of X as the first column (named "key"). Subsequent columns will be derived from the keys of the first sub-dictionary with each row populated by corresponding values from all nested dictionaries. Missing keys in any sub-dictionary will result in null values in the table.

    .. note::

        Dictionaries with more than 32,767 keys cannot be converted into a table.

    - If X is an array vector or columnar tuple: switch data from columns to rows, or vice versa.

    Parameters
    ----------
    obj : Constant
        A tuple/matrix/table/dictionary/array vector/columnar tuple.

        - If X is a tuple, all elements must be vectors of the same length.

        - If X is an array vector or columnar tuple, the number of elements in each row must be the same.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_treasuryConversionFactor)
    def treasuryConversionFactor(contractCoupon: Constant, deliverableCoupon: Constant, monthsToNextCoupon: Constant, remainingPayments: Constant, frequency: Constant) -> Constant:
        ...


@builtin_function(_triggerTSDBCompaction)
def triggerTSDBCompaction(chunkId: Constant, level: Constant = DFLT) -> Constant:
    r"""Use this command to manually trigger the compaction of TSDB level files
    at specific level for optimal reading performance.

    .. note::

        The compaction of level 3 files can only be performed when configuration
        parameter allowTSDBLevel3Compaction is set to true and for tables with
        keepDuplicates=FIRST/LAST specified.

    Parameters
    ----------
    chunkId : Constant
        A STRING scalar indicating the chunk ID.
    level : Constant, optional
        Specify at which level the compaction is triggered, by default DFLT.
        It can be an integer in [-1,3].

        - If level is an integer in [0,3], compaction is triggered at the specified level.

        - When level = -1, all level files are compacted into a single level file.
    """
    ...


@builtin_function(_tril)
def tril(X: Constant, k: Constant = DFLT) -> Constant:
    r"""If k is not specified: return the lower triangular portion of matrix X.

    If k is specified: return the elements on and below the k-th diagonal of X.

    Parameters
    ----------
    X : Constant
        A matrix.
    k : Constant, optional
        An integer, by default DFLT.
    """
    ...


@builtin_function(_trim)
def trim(X: Constant) -> Constant:
    r"""Trim all white spaces around the string.

    Parameters
    ----------
    X : Constant
        A string scalar/vector.
    """
    ...


@builtin_function(_trima)
def trima(X: Constant, window: Constant) -> Constant:
    r"""Calculate the Triangular Moving Average (trima) for X in a sliding window of the given length.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    window : Constant
        A positive integer indicating the size of the sliding window.
    """
    ...


@builtin_function(_triu)
def triu(X: Constant, k: Constant = DFLT) -> Constant:
    r"""If k is not specified: return the upper triangular portion of matrix X.

    If k is specified: return the elements on and above the k-th diagonal of X.

    Parameters
    ----------
    X : Constant
        A matrix.
    k : Constant, optional
        An integer, by default DFLT
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_trueRange)
    def trueRange(high: Constant, low: Constant, close: Constant) -> Constant:
        r"""Return a vector of the same length as each of the input vectors.

        The result for each position is the maximum of `| high - low |`,
        `| high - last period close |` and `| last period close - low |`.

        Parameters
        ----------
        high : Constant
            A numeric vector indicating the highest price of the current period.
        low : Constant
            A numeric vector indicating the lowest price of the current period.
        close : Constant
            A numeric vector indicating the closing price of the current period.

        Returns
        -------
        Constant
            A a vector of the same length as each of the input vectors.
        """
        ...


@builtin_function(_truncate)
def truncate(dbUrl: Constant, tableName: Constant) -> Constant:
    r"""Remove all rows from a DFS table but keep its schema. Command truncate is
    faster than the delete statement and the dropPartition function.

    It is suggested to call function dropTable if you want to delete the schema of the table.

    Parameters
    ----------
    dbUrl : Constant
        A string indicating the DFS path of a database.
    tableName : Constant
        A string indicating the table name.
    """
    ...


@builtin_function(_tupleSum)
def tupleSum(X: Constant) -> Constant:
    r"""Summarize individual results from multiple map calls. If each map call returns
    a tuple with N non-tuple objects, the input for tupleSum function would be a
    tuple of N tuples. Each child tuple contains m objects with identical data
    form and data type, where m is the number of map calls. If there is a single
    map call, however, tupleSum accepts the results of the map call as the input,
    and simply returns the input as the output.

    The result of the function tupleSum always has the same format as the map call
    result. If the map call returns a tuple with at least 2 non-tuple objects,
    then tupleSum returns a tuple containing the same number of non-tuple objects.

    Parameters
    ----------
    X : Constant
        A tuple.
    """
    ...


@builtin_function(_twindow)
def twindow(func: Constant, funcArgs: Constant, T: Constant, range: Constant, prevailing: Constant = DFLT, excludedPeriod: Constant = DFLT) -> Constant:
    r"""Apply func over a sliding window of funcArgs. Each element in funcArgs
    corresponds to a window that is determined by T and range. The result has
    the same dimension as that of funcArgs (If funcArgs is a tuple, the result
    has the same dimension as that of each element in the tuple).

    Suppose range is set to d1:d2, the windows are determined based on the following rules:

    - When range is an integral pair:

      - T is a vector of integral type: For element Ti in T, the window range is [Ti+d1, Ti+d2].

      - T is a vector of temporal type: range has the precision of T by default.
        For element Ti in T, the window range is [temporalAdd(Ti, d1, unit),
        temporalAdd(Ti, d2, unit)], where "unit" indicates the precision of T.

    - When range is a duration pair, T can only be a vector of temporal type.
      For element Ti in T, the window range is [temporalAdd(Ti, d1), temporalAdd(Ti, d2)].

    When the window boundary matches multiple duplicates, the prevailing parameter
    determines whether those duplicates are included in the window.

    - If prevailing = 0/false, the window includes all duplicates.

    - If prevailing = 1/true, the calculation window includes the last record of
      duplicates at the left boundary and all duplicates at the right boundary.

    - If prevailing = 2,

      - When d1 is 0, the window starts at the current record, excluding prior
        duplicates while including all duplicates at the right boundary.

      - When d2 is 0, the window ends at the current record, excluding following
        duplicates while including duplicates at the left boundary.

      - Note that prevailing and excludedPeriod cannot be set simultaneously.

    Compared with the tmoving function, twindow has more flexible windows. The
    tmoving function can be considered roughly as a special case of twindow,
    where the right boundary of the range parameter is 0 and prevailing is set
    to 0. However, when the window is measured by time, the range of the window
    is (Ti - window, Ti] or (temporalAdd(Ti, -window), Ti], where the left boundary
    is exclusive. The current record is included as the last element in the corresponding
    window, regardless of whether the following records have identical values.

    Parameters
    ----------
    func : Constant
        An aggregate function.
    funcArgs : Constant
        The argument(s) of func. If func has multiple parameters, funcArgs is a tuple.
    T : Constant
        A non-strictly increasing vector of integers or temporal type.
    range : Constant
        A data pair of INT or DURATION type (both boundaries are inclusive).
    prevailing : Constant, optional
        Can be 0/false (default), 1/true, or 2, indicating how duplicate values
        at window boundaries are handled, by default DFLT. The specific windowing
        rules for each value are introduced in Details.
    excludedPeriod : Constant, optional
        A pair of time values (of TIME, NANOTIME, MINUTE, and SECOND type)
        representing the start and end time of the period which is excluded from
        the calculation, by default DFLT.

        When the excludedPeriod is set, the input T cannot contain the time range
        specified by excludedPeriod and must be of TIMESTAMP, NANOTIMESTAMP,
        TIME, and NANOTIME types. Note that excludedPeriod must be within a calendar
        day and cannot be longer than the value of (24 - range).
    """
    ...


@builtin_function(_type)
def type(obj: Constant) -> Constant:
    r"""Return an integer indicating the data type of X. Please refer to Data Types for details.

    Parameters
    ----------
    obj : Constant
        Can be any data type that the system supports.

    Returns
    -------
    Constant
        An integer.
    """
    ...


@builtin_function(_typestr)
def typestr(obj: Constant) -> Constant:
    r"""Return a string indicating the data type of X. Please refer to Data Types for details.

    Parameters
    ----------
    obj : Constant
        Can be any data type that the system supports.

    Returns
    -------
    Constant
        A string.
    """
    ...


@builtin_function(_undef)
def undef(obj: Constant, objType: Constant = DFLT, objAddr: Constant = DFLT) -> Constant:
    r"""Release variables or function definitions from the memory. You can also
    release a local variable (VAR) from the memory using "= NULL".

    Parameters
    ----------
    obj : Constant
        A string or a string vector indicating the names of objects to be undefined.
        To undefine all the variables in a category, use the unquoted "all" for obj.
    objType : Constant, optional
        Type of objects to be undefined. The types can be: VAR (variable),
        SHARED (shared variable) or DEF (function definition), by default DFLT.

        To delete all user-defined objects in the system except shared variables, use "undef all".
    objAddr : Constant, optional
        _description_, by default DFLT
    """
    ...


@builtin_function(_ungroup)
def ungroup(X: Constant) -> Constant:
    r"""For table X, where some columns are array vectors or columnar tuples,
    returns the normalized table, with one row for each element of the flattened
    array vector or columnar tuple.

    If X does not contain array vectors or columnar tuples or the number of rows
    for X is 0, returns X directly.

    Parameters
    ----------
    X : Constant
        A table object.
    """
    ...


@builtin_function(_unifiedCall)
def unifiedCall(func: Constant, args: Constant) -> Constant:
    r"""Call a function with the specified parameters. Similar to call, it can be
    used in each/peach or loop/ploop to call a set of functions. The difference
    is that the size of args in call function is determined by the function passed
    in by the parameter func, whereas the size of args in unifiedCall is always 1.
    All arguments of the function used in function call is assembled in a tuple
    for function unifiedCall.

    Parameters
    ----------
    func : Constant
        A function.
    args : Constant
        A uple. Each element is a parameter of func.
    """
    ...


@builtin_function(_unifiedExpr)
def unifiedExpr(objs: Constant, optrs: Constant) -> Constant:
    r"""Connect the operands in objs with the binary operators in optrs to generate
    metacode of a multivariate expression. You can execute the metacode with function eval.

    Parameters
    ----------
    objs : Constant
        A Tuple with a length between 2 and 1024 (inclusive).
    optrs : Constant
        A vector of binary operators and the length is size(objs)-1.
    """
    ...


@builtin_function(_union)
def union(X: Constant, Y: Constant) -> Constant:
    r"""Return the union of two sets.

    Parameters
    ----------
    X : Constant
        A set.
    Y : Constant
        A set.

    Returns
    -------
    Constant
        A set.
    """
    ...


@builtin_function(_unionAll)
def unionAll(tableA: Union[Alias[Literal["tables"]], Constant], tableB: Union[Alias[Literal["partition"]], Constant] = DFLT, byColName: Constant = DFLT) -> Constant:
    r"""For the first scenario, combine 2 tables into a single table. The result
    is an unpartitioned in-memory table.

    For the second scenario, combine multiple tables into a single table.
    If partitioned is set to "false", the result is an unpartitioned in-memory table;
    if partitioned is set to "true", the result is a partitioned in-memory table
    with sequential domain. The default value is "true".

    If byColName =false, all tables to be combined must have identical number of columns.

    If byColName =true, the tables to be combined can have different number of columns.
    If a column does not exist in a table, it is filled with null values in the final result.

    Parameters
    ----------
    tableA : Union[Alias[Literal[&quot;tables&quot;]], Constant]
        A table.
    tableB : Union[Alias[Literal[&quot;partition&quot;]], Constant], optional
        A table, by default DFLT
    byColName : Constant, optional
        A Boolean value indicating whether the table combination is conducted along
        columns with the same name, by default DFLT.
    """
    ...


@builtin_function(_unpack)
def unpack(format: Constant, buffer: Constant) -> Constant:
    r"""Unpack from the buf according to the format string specified by format.
    The result is a tuple with the unpacked data even if it contains exactly one item.

    Parameters
    ----------
    format : Constant
        A format string.

        - A format character may be preceded by an integral repeat count.
          For example, the format string '4h' means exactly the same as 'hhhh'.

        - Whitespace characters between formats are ignored; a count and its
          format must not contain whitespace though.

        - For the 's' format character, the count is interpreted as the length of
          the bytes, not a repeat count like for the other format characters;
          for example, '10s' means a single 10-byte string, while '10c' means 10 characters.
          If a count is not given, it defaults to 1. The string is truncated or
          padded with null bytes as appropriate to make it fit.
    buffer : Constant
        A bytes object of STRING or BLOB type. The size of buf in bytes must
        match the size required by the format.
    """
    ...


@builtin_function(_unpivot)
def unpivot(obj: Constant, keyColNames: Constant, valueColNames: Constant, func: Constant = DFLT) -> Constant:
    r"""Convert the columns specified by valueColNames into a single column.


    Parameters
    ----------
    obj : Constant
        A table.
    keyColNames : Constant
        A STRING scalar/vector indicating column name(s).
    valueColNames : Constant
        A vector of column names. The specified columns will be converted into a
        single column. Note the values in these columns must have the same data type.
    func : Constant, optional
        Indicate a function that is applied to valueColNames before they're converted
        into one column, by default DFLT

    Returns
    -------
    Constant
        Return a table with columns arranged in the following order: the columns
        specified by keyColNames, the "valueType" column, and the "value" column:

        - The "valueType" column holds the results of func applied on the columns
          specified by valueColNames if func is specified, otherwise "valueType"
          holds the column names specified by valueColNames.

        - The "value" column holds the corresponding values of these columns.
    """
    ...


@builtin_function(_update_)
def update_(table: Constant, colNames: Constant, newValues: Constant, filter: Constant = DFLT) -> Constant:
    r"""Update columns of a table in place. If a column in colNames doesn't exist,
    create a new column; otherwise update the existing column. If a filter is
    specified, only rows satisfying the filtering condition will be updated.

    This operation is parallel if the table is a partitioned table and if the
    parallel processing feature is enabled (when the configuration parameter localExcutors > 0).

    Parameters
    ----------
    table : Constant
        A DolphinDB table. It can be a partitioned in-memory table.
    colNames : Constant
        A string scalar/vector indicating the columns to be updated.
    newValues : Constant
        A piece of metacode with the operations for the specified columns.
        Metacode is objects or expressions within "<" and ">". For details about
        metacode, please refer to Metaprogramming.
    filter : Constant, optional
        A a piece of metacode with filterting conditions, by default DFLT.
    """
    ...


@builtin_function(_updateLicense)
def updateLicense() -> Constant:
    r"""Update the license without restarting the node.

    After replacing the license file, executing this function can update the license without restarting the node. You can execute getLicenseExpiration to check whether the license file has been updated.

    The function only takes effect on the node where it is executed. For a cluster, it must be executed on all controllers, agents, and data nodes.

    .. note::

        - The license for update must satisfy the following conditions (which can be checked with function license):

          - The client name (clientName) and the authorization mode (authorization) of the license must be the same as the original license.

          - The number of nodes (maxNodes), memory size (maxMemoryPerNode) and the number of CPU cores (maxCoresPerNode) authorized by the license cannot be smaller than the original ones.

        - Online update is not supported if the original authorization is site.

        - DolphinDB process can be bound to specific CPU cores. If the binding cores are changed in the license to be replaced, DolphinDB must be rebooted after the upgrade.
    """
    ...


@builtin_function(_upper)
def upper(X: Constant) -> Constant:
    r"""Convert all characters in a string or a list of strings into upper cases.

    Parameters
    ----------
    X : Constant
        A string scalar/vector.
    """
    ...


@builtin_function(_upsert_)
def upsert_(obj: Constant, newData: Constant, ignoreNull: Constant = DFLT, keyColNames: Constant = DFLT, sortColumns: Constant = DFLT) -> Constant:
    r"""Insert rows into a keyed table or indexed table if the values of the primary
    key do not already exist, or update them if they do.

    .. note::

        - When using this function, please make sure the corresponding columns in table
          newData and obj are arranged in the same order, or the system may generate the
          wrong result or throw an error.

        - If obj is a DFS table with duplicated "keys" (as specified by keyColNames),
          `upsert_` on rows with duplicated keys only updates the first row.

        - The behavior of this function is controlled by the enableNullSafeJoin configuration:

        - When enableNullSafeJoin=true, joining on null values is allowed, and
          `upsert_` may update records that contain nulls.

        - When enableNullSafeJoin=false, joining on null values is not allowed, and
          `upsert_` will not update records with nulls.

    Parameters
    ----------
    obj : Constant
        A keyed table, indexed table, or a DFS table.
    newData : Constant
        An in-memory table.
    ignoreNull : Constant, optional
        A oolean value, by default DFLT. If set to true, for the null values in
        newData, the corresponding elements in obj are not updated. The default value is false.
    keyColNames : Constant, optional
        A STRING scalar/vector. When obj is a DFS table, keyColNames and the partitioning
        columns are considered as the key columns, by default DFLT.
    sortColumns : Constant, optional
        A STRING scalar or vector, by default DFLT. The updated partitions will be
        sorted on sortColumns (only within each partition, not across partitions).
    """
    ...


@builtin_function(_uuid)
def uuid(X: Constant) -> Constant:
    r"""Convert STRING into UUID data type.

    Parameters
    ----------
    X : Constant
        A STRING scalar/vector.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_valueAtRisk)
    def valueAtRisk(returns: Constant, method: Constant, confidenceLevel: Constant = DFLT) -> Constant:
        r"""Calculate Value at Risk (VaR) to predict the minimum return within a
        given confidence level (e.g. 95% or 99%) over a specific time frame.

        Parameters
        ----------
        returns : Constant
            A numeric vector representing the returns. The element must be
            greater than -1 and cannot be empty.
        method : Constant
            A string indicating the VaR calculation method, which can be:

            - 'normal': parametric method with normal distribution.

            - 'logNormal': parametric method with log-normal distribution.

            - 'historical': historical method.

            - 'monteCarlo': Monte Carlo simulation.
        confidenceLevel : Constant, optional
            A numeric scalar representing the confidence level, with a valid range of (0,1),
            by default DFLT.

        Returns
        -------
        Constant
            A DOUBLE value indicating the absolute value of the minimum return.
        """
        ...


@builtin_function(_valueChanged)
def valueChanged(X: Constant, mode: Constant = DFLT) -> Constant:
    r"""Compare each element in X with the element specified by mode. Return true
    if the value is changed, otherwise false. Return false if the compared object does not exist.

    For example, for the first element of valueChanged(X, [mode="prev"]) and the
    last element of valueChanged(X, [mode="next"]), the function returns false.

    If X is a matrix/table, perform the aforementioned operation on each column
    and return a matrix/table.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table/tuple of STRING, BOOL, temporal or numeric type.
    mode : Constant, optional
        A string, by default DFLT. It can take the value of "prev", "next", "either" and "both".

        - "prev": the previous element

        - "next": the next element

        - "either": the previous OR the next element

        - "both": the previous AND the next element
    """
    ...


@builtin_function(_values)
def values(obj: Constant) -> Constant:
    r"""Return all values of a dictionary, or all the columns of a table in a tuple.

    Parameters
    ----------
    obj : Constant
        A dictionary/table.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_vanillaOption)
    def vanillaOption(settlement: Constant, maturity: Constant, evalDate: Constant, spot: Constant, strike: Constant, riskFree: Constant, divYield: Constant, volatility: Constant, isCall: Constant, style: Constant, basis: Constant, calendar: Constant, method: Constant = DFLT, kwargs: Constant = DFLT, mode: Constant = DFLT) -> Constant:
        r"""Calculate vanilla option prices using specified methods.

        Parameters
        ----------
        settlement : Constant
            A DATE scalar or vector indicating the settlement date.
        maturity : Constant
            A DATE scalar or vector indicating the maturity date.
        evalDate : Constant
            A DATE scalar or vector indicating the evaluation date.
        spot : Constant
            A numeric scalar or vector indicating the spot price.
        strike : Constant
            A numeric scalar or vector indicating the strike price.
        riskFree : Constant
            A numeric scalar or vector indicating the risk-free interest rate.
        divYield : Constant
            A numeric scalar or vector indicating the dividend yield.
        volatility : Constant
            A numeric scalar or vector indicating the volatility.
        isCall : Constant
            A Boolean scalar or vector.

            - true: buy (call option)

            - false: sell (put option)
        style : Constant
            A STRING scalar or vector indicating the option exercise style.
            It can be 'european' or 'american'.
        basis : Constant
            An integer or STRING scalar or vector specifying the day count basis type.
            The optional values are:

            +----------------------+---------------------+
            | Basis                | Day Count Basis     |
            +======================+=====================+
            | 0 / "Thirty360US"    | US (NASD) 30/360    |
            +----------------------+---------------------+
            | 1 / "ActualActual"   | actual/actual       |
            | (default)            |                     |
            +----------------------+---------------------+
            | 2 / "Actual360"      | actual/360          |
            +----------------------+---------------------+
            | 3 / "Actual365"      | actual/365          |
            +----------------------+---------------------+
            | 4 / "Thirty360EU"    | European 30/360     |
            +----------------------+---------------------+

        calendar : Constant
            A STRING scalar or vector indicating the trading calendar(s).
            See Trading Calendar for more information.
        method : Constant, optional
            A STRING scalar indicating the pricing method, by default DFLT.

            - 'BS' (default): Black-Scholes model (for European options only).

            - 'FDBS': Finite Difference method + Black-Scholes model.

            - 'heston': Heston model (for European options only).

            - 'FDHeston': Finite Difference method + Heston model.

            - 'PTDHeston': Piecewise Time Dependent Heston model (for European options only).
        kwargs : Constant, optional
            A dictionary specifying other required parameters. Leave it unspecified
            when method='BS', by default DFLT. The key-values pairs should be:

            - When method='FDBS':

              - 'xGrid': A scalar or vector with integers greater than 1, indicating the number of spatial grids used for discretization in the finite difference method.

              - 'tGrid': A scalar or vector with positive integers, indicating the number of time grids used for discretization in the finite difference method. tGrid must be greater than 0.

              - 'dampingSteps': A scalar or vector with non-negative integers, representing the number of damping steps applied in the finite difference solution process.
            - When method='heston':

              - 'theta': A numeric scalar or vector representing the long-term mean of the variance.

              - 'kappa': A numeric scalar or vector indicating the speed of mean reversion for the variance.

              - 'rho': A numeric scalar or vector representing the correlation coefficient between the asset price and volatility.

              - 'sigma': A numeric scalar or vector representing the volatility of volatility.
            - When method='FDHeston':

              - 'theta': A numeric scalar or vector representing the long-term mean of the variance.

              - 'kappa': A numeric scalar or vector indicating the speed of mean reversion for the variance.

              - 'rho': A numeric scalar or vector representing the correlation coefficient between the asset price and volatility.

              - 'sigma': A numeric scalar or vector representing the volatility of volatility.

              - 'xGrid': An scalar or vector with integers greater than 1, indicating the number of spatial grids used for discretization in the finite difference method.

              - 'vGrid': An scalar or vector with integers greater than 1, indicating the number of volatility grids used for discretization in the finite difference method.

              - 'tGrid': An scalar or vector with positive integers, indicating the number of time grids used for discretization in the finite difference method. tGrid must be greater than 0.

              - 'dampingSteps': An scalar or vector with non-negative integers, representing the number of damping steps applied in the finite difference solution process.
            - When method='PTDHeston':

              - 'times': A numeric vector or array indicating the time points when conditions change.

              - 'theta': A numeric scalar or vector representing the long-term mean of the variance.

              - 'kappa': A numeric scalar or vector indicating the speed of mean reversion for the variance.

              - 'rho': A numeric scalar or vector representing the correlation coefficient between the asset price and volatility.

              - 'sigma': A numeric scalar or vector representing the volatility of volatility.
        mode : Constant, optional
            An integeralscalar or vector indicating the output mode, by default DFLT.
            It can be:

            - 0: NPV (net present value) only.

            - 1: NPV and Greeks (delta, gamma, theta, vega and rho) in a nested tuple.

            - 2: NPV and Greeks (delta, gamma, theta, vega and rho) in an ordered dictionary.

        Returns
        -------
        Constant
            - When mode=0, return a FLOATING scalar or vector indicating the NPV.

            - When mode=1, return a tuple with two tuple elements, NPV and Greeks (delta, gamma, theta, vega and rho).

            - When mode=2, return an ordered dictionary with keys 'npv', 'delta', 'gamma', 'theta', 'vega', and 'rho'.
        """
        ...


@builtin_function(_var)
def var(X: Constant) -> Constant:
    r"""If X is a vector, return the the (unbiased) sample standard variance of X.

    If X is a matrix, calculate the the (unbiased) sample standard variance of each column of X and return a vector.

    As with all aggregate functions, null values are not included in the calculation.

    .. note::

        The result is sample variance instead of population variance.

    Parameters
    ----------
    X : Constant
        A scalar/vector/matrix.
    """
    ...


if not sw_is_ce_edition():
    @builtin_function(_varma)
    def varma(ds: Constant, endogColNames: Constant, order: Constant, exog: Constant = DFLT, trend: Constant = DFLT, errorCovType: Constant = DFLT, measurementError: Constant = DFLT, enforceStationarity: Constant = DFLT, enforceInvertibility: Constant = DFLT, trendOffset: Constant = DFLT, maxIter: Constant = DFLT) -> Constant:
        r"""Analyze multivariate time series using a Vector Autoregressive
        Moving-Average (VARMA) model. It returns a dictionary containing the analysis results.

        Parameters
        ----------
        ds : Constant
            An in-memory table or a DATASOURCE vector containing the multivariate
            time series to be analyzed. ds cannot be empty. Only if the first column
            of the data source is a time column, the model will automatically
            sort the data based on the column.
        endogColNames : Constant
            A STRING vector indicating the column names of the endogenous variables in ds.
        order : Constant
            A vector with two non-negative integers indicating the number of
            autoregressive (AR) and moving average (MA) parameters to use.
        exog : Constant, optional
            A numeric matrix representing exogenous variables except the endogenous
            time series, by default DFLT. Each column of the matrix represents the
            time series data of an exogenous variable, and the number of rows
            must equal the number of rows in ds.
        trend : Constant, optional
            A string indicating the constant and trend order used in the regression,
            by default DFLT. Possible values:

            - "c" (default) - add constant

            - "ct" - constant and treand

            - "ctt" - constant, linear, and quadratic trend

            - "n" - no constant or trend
        errorCovType : Constant, optional
            A STRING scalar specifying the structure of the error term's covariance
            matrix, by default DFLT. Possible values:

            - 'unstructured' (default): Preserve the lower triangular part of the covariance matrix

            - 'diagonal': Preserve only the diagonal part
        measurementError : Constant, optional
            A boolean scalar indicating whether to assume the endogenous observations
            were measured with error, by default DFLT.
        enforceStationarity : Constant, optional
            A boolean scalar indicating whether to transform AR parameters to enforce
            stationarity in the autoregressive component of the model, by default DFLT.
        enforceInvertibility : Constant, optional
            A boolean scalar indicating whether to transform MA parameters to enforce
            invertibility in the moving average component of the model, by default DFLT.
        trendOffset : Constant, optional
            A positive representing the offset at which time trend values start,
            by default DFLT.
        maxIter : Constant, optional
            A positive integer indicating the maximum number of iterations during
            fitting, by default DFLT.

        Returns
        -------
        Constant
            A dictionary containing the following keys:

            - params: A floating matrix of estimated parameters for the VARMA model.

            - kAr: An integer representing the order of the vector autoregressive process.

            - kMa: An integer representing the order of the vector moving average part.

            - kTrend: An integer representing the number of trend terms in the VARMA model.

            - nobs: An integer representing the number of observations in the input multivariate time series.

            - aic: A floating-point number representing the Akaike Information Criterion.

            - bic: A floating-point number representing the Bayesian Information Criterion.

            - hqic: A floating-point number representing the Hannan-Quinn Information Criterion.

            - llf: A floating-point number representing the log-likelihood value of the VARMA model.
        """
        ...


@builtin_function(_varp)
def varp(X: Constant) -> Constant:
    r"""If X is a vector, return the population variance of X.

    If X is a matrix, ccalculate the population variance of each column and return a vector.

    As with all other aggregate functions, null values are ignored in the calculation.

    Parameters
    ----------
    X : Constant
        A vector/matrix.
    """
    ...


@builtin_function(_vectorAR)
def vectorAR(ds: Constant, endogColNames: Constant, exog: Constant = DFLT, trend: Constant = DFLT, maxLag: Constant = DFLT, ic: Constant = DFLT) -> Constant:
    r"""Analyze multivariate time series using the Vector Autoregression model (VAR model).

    Parameters
    ----------
    ds : Constant
        An in-memory table or a vector consisting of DataSource objects,
        containing the multivariate time series to be analyzed. ds cannot be empty.
    endogColNames : Constant
        A STRING vector indicating the column names of the endogenous variables
        in ds. The matrix formed by endogColNames extracted from ds is the
        multivariate time series to be analyzed.
    exog : Constant, optional
        A numeric matrix representing exogenous variables except the endogenous
        time series, by default DFLT. Each column of the matrix represents the
        time series data of an exogenous variable, and the number of rows must
        equal the number of rows in ds.
    trend : Constant, optional
        Specify constants and trend orders used in the regression, by default DFLT.  It can be

        - 'c' (default) - add constant

        - 'ct' - constant and treand

        - 'ctt' - constant, linear, and quadratic trend

        - 'n' - no constant or trend
    maxLag : Constant, optional
        A non-negative integer representing the maximum number of lags to check
        for order selection, by default DFLT.
    ic : Constant, optional
        A  STRING scalar indicating the information criterion to use for VAR order
        selection, by default DFLT. It can be:

        - 'aic': Akaike

        - 'bic': Bayesian/Schwarz

        - 'fpe': Final prediction error

        - 'hqic': Hannan-Quinn

    Returns
    -------
    Constant
        A dictionary representing the analysis results of the VAR model with the following members:

        - params: A floating-point matrix representing the parameters obtained from fitting the VAR model.

        - kAr: An integer representing the order of the VAR process.

        - kTrend: An integer representing the number of trends in the VAR process.

        - nobs: An integer representing the number of observations in the VAR model analysis.

        - sigmaU: A floating-point matrix representing the estimated variance of the white noise process.

        - sigmaUMle: A floating-point matrix representing the biased maximum likelihood estimate of the noise process covariance.

        - aic: A floating-point scalar representing the Akaike Information Criterion.

        - bic: A floating-point scalar representing the Bayesian Information Criterion.

        - hqic: A floating-point scalar representing the Hannan-Quinn Information Criterion.

        - fpe: A floating-point scalar representing the Final Prediction Error Information Criterion.

        - llf: A floating-point scalar representing the log-likelihood value of the VAR model.
    """
    ...


@builtin_function(_vectorNorm)
def vectorNorm(x: Constant, ord: Constant = DFLT, axis: Constant = DFLT, keepDims: Constant = DFLT) -> Constant:
    r"""Compute a matrix or vector norm. Note that it’s not recommended to use
    vectorNorm in SQL statements.


    Parameters
    ----------
    x : Constant
        A vector or matrix of any numeric type except DECIMAL. It cannot be empty.
    ord : Constant, optional
        An INT, STRING or floating-point scalar indicating the order of norm, by default DFLT.

        .. note::

            When ord is a string, it must be: 'inf', '-inf', 'nuc', or 'fro'.

            When ord is less than 1, the result is technically not a mathematical
            "norm", but it may still be useful for various numerical purposes.

        The following describes the method for computing the norm based on different x and ord:

        +--------+-------------------------------+------------------------------------------+
        | ord    | norm for vectors              | norm for matrices                        |
        +========+===============================+==========================================+
        | None   | 2-norm                        | Frobenius norm                           |
        +--------+-------------------------------+------------------------------------------+
        | 0      | sum(x != 0)                   | &#45                                     |
        +--------+-------------------------------+------------------------------------------+
        | -1     | sum(abs(x)^ord)^(1/ord)       | min(sum(abs(x), axis=0))                 |
        +--------+-------------------------------+------------------------------------------+
        | 1      | sum(abs(x)^ord)^(1/ord)       | max(sum(abs(x), axis=0))                 |
        +--------+-------------------------------+------------------------------------------+
        | -2     | sum(abs(x)^ord)^(1/ord)       | 2-norm (largest sing. value)             |
        +--------+-------------------------------+------------------------------------------+
        | 2      | sum(abs(x)^ord)^(1/ord)       | smallest singular value                  |
        +--------+-------------------------------+------------------------------------------+
        | inf    | max(abs(x))                   | max(sum(abs(x), axis=1))                 |
        +--------+-------------------------------+------------------------------------------+
        | -inf   | min(abs(x))                   | min(sum(abs(x), axis=1))                 |
        +--------+-------------------------------+------------------------------------------+
        | nuc    | &#45                          | nuclear norm                             |
        +--------+-------------------------------+------------------------------------------+
        | fro    | &#45                          | Frobenius norm                           |
        +--------+-------------------------------+------------------------------------------+
        | other  | sum(abs(x)^ord)^(1/ord)       | &#45                                     |
        +--------+-------------------------------+------------------------------------------+

    axis : Constant, optional
        An integer vector or scalar indicating the direction along which to compute
        the norm, by default DFLT. It cannot contain empty elements.

        - When x is a vector, axis can only be 0.

        - When x is a matrix, axis:

        - Has a length of no more than 2.

        - Cannot contain duplicate elements.

        - Has elements with values of 0 or 1.
    keepDims : Constant, optional
        A  boolean scalar indicating whether the returned result should maintain
        the same form as x, by default DFLT.

    Returns
    -------
    Constant
        An INT, LONG, or DOUBLE scalar, vector, or matrix.
    """
    ...


@builtin_function(_version)
def version() -> Constant:
    r"""Return key system information about the DolphinDB server:

    - Version number

    - Release date

    - Operating system

    - CPU instruction set

    - Compiler version (for JIT/ABI only)

    Returns
    -------
    Constant
        A string.
    """
    ...


@builtin_function(_volumeBar)
def volumeBar(X: Constant, interval: Constant, label: Constant = DFLT) -> Constant:
    r"""This function sequentially accumulates the elements in X, and then groups
    them based on the specified threshold. Once a group is determined, the accumulation
    starts from the next element and data grouping is performed in the same logic.
    It returns a vector of the same size as X containing the corresponding group
    number for each element.

    Elements are divided into groups based on the threshold specified by interval.

    - If interval is positive, elements are labeled into groups when the cumulative sum is no smaller than the threshold;

      - If interval is in (0, 1), the threshold is sum(X) * interval. Note that the threshold is converted to the same data type as X for comparison. For example, if X is an integer, then the threshold will be set at floor(sum(X) * interval).

      - Otherwise, the threshold takes the value of interval.

    - If interval is negative, the threshold takes the value of interval. Elements are labeled into groups when the cumulative sum is no greater than the threshold.

    Parameters
    ----------
    X : Constant
        A numeric vector.
    interval : Constant
        A non-zero number that represents a constant value or percentage that
        determines the threshold for data grouping.
    label : Constant, optional
        A string used to label the groups, by default DFLT.  It can be:

        - 'seq'(default): label the groups with a sequence of 0, 1, 2, 3...

        - 'left': label each group with the sum of all elements before the first element in the group. The first group is labeled with 0.

        - 'right': label each group with the sum of all elements up to and including the last element in the group.
    """
    ...


@builtin_function(_wavg)
def wavg(X: Constant, Y: Constant) -> Constant:
    r"""Calculate the weighted average of X with the weight vector Y.
    Please note that the weight vector Y is automatically scaled such that the
    sum of the weights is 1.

    Parameters
    ----------
    X : Constant
        The value vector.
    Y : Constant
        The weight vector.
    """
    ...


@builtin_function(_wc)
def wc(X: Constant) -> Constant:
    r"""Count the words in X.

    Parameters
    ----------
    X : Constant
        A string scalar/vector.
    """
    ...


@builtin_function(_wcovar)
def wcovar(X: Constant, Y: Constant, W: Constant) -> Constant:
    r"""Calculate the weighted covariance of X and Y with weights as the weight vector.

    Parameters
    ----------
    X : Constant
        A vector.
    Y : Constant
        A vector.
    W : Constant
        A vector.
    """
    ...


@builtin_function(_weekBegin)
def weekBegin(X: Constant, weekday: Constant = DFLT, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""For each element of X, return the first date of the week that it belongs
    to and that starts on the day as specified by parameter weekday.

    - If parameter weekday>weekday(X, false): for each element of X, return a date
      that corresponds to the specified weekday parameter in the previous calendar week.

    - If parameter weekday<=weekday(X, false): for each element of X, return a date
      that corresponds to the specified weekday parameter in the same calendar week.

    If parameter offset is specified, the result is updated every n weeks. Please
    refer to example 2 below. The parameters offset and n must be specified together,
    and offset takes effect only when n > 1.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type DATE, DATETIME, DATEHOUR, TIMESTAMP or NANOTIMESTAMP.
    weekday : Constant, optional
        An integer from 0 to 6. 0 means Monday, 1 means Tuesday, ..., and 6
        means Sunday, by default DFLT.
    offset : Constant, optional
        A scalar of the same data type as X. It must be no greater than the minimum
        value of X, by default DFLT.
    n : Constant, optional
        A positive integer, by default DFLT
    """
    ...


@builtin_function(_weekEnd)
def weekEnd(X: Constant, weekday: Constant = DFLT, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""For each element of X, return the last date of the week that it belongs
    to and that ends on the day as specified by parameter weekday.

    - If parameter weekday>=weekday(X, false): for each element of X, return a date
      that corresponds to the specified "weekday" parameter in the same calendar week.

    - If parameter weekday<weekday(X, false): for each element of X, return a date
      that corresponds to the specified "weekday" parameter in the next calendar week.

    If parameter offset is specified, the result is updated every n weeks. The
    parameters offset and n must be specified together, and offset takes effect only when n > 1.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type DATE, DATETIME, DATEHOUR, TIMESTAMP or NANOTIMESTAMP.
    weekday : Constant, optional
        An integer from 0 to 6. 0 means Monday, 1 means Tuesday, ..., and 6 means
        Sunday, by default DFLT.
    offset : Constant, optional
        A scalar of the same data type as X. It must be no greater than the minimum
        value of X, by default DFLT.
    n : Constant, optional
        A positive integer, by default DFLT.
    """
    ...


@builtin_function(_weekOfMonth)
def weekOfMonth(X: Constant, week: Constant = DFLT, weekday: Constant = DFLT, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""In the calendar month of X, suppose the "week"-th "weekday" is d.

    - If X<d: return the week-th "weekday" in the previous calendar month.

    - If X>=d: return the week-th "weekday" in the current calendar month.

    If parameter offset is specified, the result is updated every n months.
    Parameter offset works only if parameter n>1.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type DATE, DATETIME, DATEHOUR, TIMESTAMP or NANOTIMESTAMP.
    week : Constant, optional
        An integer from 0 to 3 indicating the i-th week of a month, by default DFLT.
    weekday : Constant, optional
        An integer from 0 to 6. 0 means Monday, 1 means Tuesday, ..., and 6 means
        Sunday, by default DFLT.
    offset : Constant, optional
        A scalar of the same data type as X. It must be no greater than the
        minimum value of X, by default DFLT.
    n : Constant, optional
        A positive integer, by default DFLT.
    """
    ...


@builtin_function(_weekOfYear)
def weekOfYear(X: Constant) -> Constant:
    r"""Return the week number for X.

    .. note::

        - Each week starts on Sunday. The first week of the year has more than 4 days.

        - If 31 December is on a Monday, Tuesday or Wednesday, it is in week 01 of the next year. If it is on a Thursday, it is in week 53 of the year just ending; if on a Friday it is in week 52 (or 53 if the year just ending is a leap year); if on a Saturday or Sunday, it is in week 52 of the year just ending.

    Parameters
    ----------
    X : Constant
        A scalar/vector of type DATE, DATETIME, DATEHOUR, TIMESTAMP or NANOTIMESTAMP.
    """
    ...


@builtin_function(_weekday)
def weekday(X: Constant, startFromSunday: Constant = DFLT) -> Constant:
    r"""eturn integer(s) to represent of the corresponding weekday(s) of X.

    If startFromSunday=true, 0 means Sunday, 1 means Monday, ..., and 6 means Saturday.

    If startFromSunday=false, 0 means Monday, 1 means Tuesday, ..., and 6 means Sunday.

    Parameters
    ----------
    X : Constant
        A temporal scalar/vector.
    startFromSunday : Constant, optional
        A Boolean value indicating whether a week starts from Sunday, by default DFLT.
        If startFromSunday=false, a week starts from Monday.
    """
    ...


@builtin_function(_wilder)
def wilder(X: Constant, window: Constant) -> Constant:
    r"""Calculate the Exponential Moving Average (ema) for X in a sliding window of the given length.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    window : Constant
        A positive integer indicating the size of the sliding window.
    """
    ...


@builtin_function(_window)
def window(func: Constant, funcArgs: Constant, range: Constant) -> Constant:
    r"""Apply func over a sliding window of funcArgs. Each element in funcArgs
    corresponds to a window that is determined by range. The result has the same
    dimension as that of funcArgs (If funcArgs is a tuple, the result has the same
    dimension as that of each element in the tuple).

    Suppose range is set to d1:d2, the windows are determined based on the following rules:

    - When funcArgs is a vector, range must be a pair of integers. For the ith element
      in funcArgs, the corresponding window contains elements at position [i+d1, i+d2].

    - When funcArgs is an indexed series or indexed matrix:

      - If funcArgs is indexed by time, for fi (the ith element in the index of funcArgs),
        the corresponding window contains elements at index [temporalAdd(fi, d1), temporalAdd(fi, d2)].

      - If funcArgs is indexed by integral values, range must also be integral.
        For fi (the ith element in the index of funcArgs), the corresponding
        window contains elements at index [fi+d1, fi+d2].

    Compared with the moving function, the window function has a more flexible window.
    moving can be roughly considered as a special case of window, where the right
    boundary of the range parameter is 0. However, please note the following differences:

    - When the window is based on element counts, moving returns null when the
      number of windowed elements does not satisfy the minPeriods, whereas window
      does not have a minimum count requirement.

    - When the window is based on time, the left boundary of the window of
      moving is exclusive and the right boundary is inclusive; whereas both
      boundaries of the window of window are inclusive. In this example:

    Suppose a window with the size of "3d" slides over an index of DATETIME type
    to apply calculation. For the point "2022.01.05T09:00:00" in the index, the
    range of the corresponding window in moving is (2022.01.02T09:00:00,2022.01.05T09:00:00],
    whereas it's [2022.01.03T09:00:00,2022.01.05T09:00:00] in window
    (with the range parameter specified as "-2d:0d").

    Parameters
    ----------
    func : Constant
        An aggregate function.
    funcArgs : Constant
        The argument(s) of func. It is a tuple if there are more than one parameter of func.
    range : Constant
        A pair of integers or duration values (both boundaries are inclusive).

        .. note::

            If range is of DURATION type, funcArgs must be an indexed matrix or an indexed series.

    Returns
    -------
    Constant
        A vector with the same type as the first window computation result.
    """
    ...


@builtin_function(_winsorize)
def winsorize(X: Constant, limit: Constant, inclusive: Constant = DFLT, nanPolicy: Constant = DFLT) -> Constant:
    r"""Return a winsorized version of the input array. For in-place modification, use winsorize_.

    Parameters
    ----------
    X : Constant
        A vector.
    limit : Constant
        A scalar or a vector with 2 elements indicating the percentages to cut
        on each side of X, with respect to the number of unmasked data, as floats
        between 0 and 1, by default DFLT.

        - If *limit* is a scalar, it means the percentages to cut on both sides of X.

        - If *limit* has n elements (including null values), the (n * limit[0])-th
          smallest element and the (n * limit[1])-th largest element are masked, and
          the total number of unmasked data after trimming is n * (1-sum(limit)).
          The value of one element of limit can be set to 0 to indicate no masking
          is conducted on this side.
    inclusive : Constant, optional
        A Boolean type scalar or a vector of 2 elements indicating whether the
        number of data being masked on each side should be truncated (true) or rounded (false)
    nanPolicy : Constant, optional
        A string indicating how to handle null values, by default DFLT. The following
        options are available (default is 'upper'):

        - 'upper': allows null values and treats them as the largest values of X.

        - 'lower': allows null values and treats them as the smallest values of X.

        - 'raise': throws an error.

        - 'omit': performs the calculations without masking null values.
    """
    ...


@builtin_function(_winsorize_)
def winsorize_(X: Constant, limit: Constant, inclusive: Constant = DFLT, nanPolicy: Constant = DFLT) -> Constant:
    r"""Winsorize the input array. For details, see winsorize. The exclamation
    mark (_) means in-place change in DolphinDB.
    """
    ...


@builtin_function(_withNullFill)
def withNullFill(func: Constant, X: Constant, Y: Constant, fillValue: Constant) -> Constant:
    r"""If only 1 of the elements at the same location of x and y is null, replace
    the null value with fillValue in the calculation. If both elements at the
    same location of x and y are null, return NULL.

    Parameters
    ----------
    func : Constant
        A  DolphinDB built-in function with two inputs, such as \+, \-, \*, \/, \\, \%,
        pow, and, or, etc.
    X : Constant
        A vector/matrix.
    Y : Constant
        A vector/matrix.
    fillValue : Constant
        A scalar.
    """
    ...


@builtin_function(_wj)
def wj(leftTable: Constant, rightTable: Constant, window: Constant, aggs: Constant, matchingCols: Constant, rightMatchingCols: Constant = DFLT) -> Constant:
    r"""Window join is a generalization of asof join. For each row in leftTable,
    window join applies aggregate functions on a matching interval of rows in rightTable .

    Similar to asof join, if there is only 1 joining column, the window join
    function assumes the right table is sorted on the joining column. If there
    are multiple joining columns, the window join function assumes the right
    table is sorted on the last joining column within each group defined by
    the other joining columns. The right table does not need to be sorted by
    the other joining columns. If these conditions are not met, unexpected
    results may be returned. The left table does not need to be sorted.

    **Standard windows (i.e., window = w1:w2):**

    The windows over the right table are determined by the current timestamp in
    the left table and the specified parameter window. Suppose the current timestamp
    in the left table is t, and window is set to w1:w2, then the corresponding window
    in the right table consists of records with timestamps in [t+w1, t+w2]. The
    function applies aggs to the selected rows in rightTable and returns the
    result for each window.

    **Special windows (i.e., window = 0:0):**

    The special window is only supported for wj.

    The windows over the right table are determined by the current timestamp in
    the left table and its previous timestamp. Suppose the current timestamp in
    the left table is t and the previous timestamp is t0, then the corresponding
    window in the right table consists of records with timestamps in [t0, t).

    The differences between wj and pwj are:

    - If rightTable doesn't have a matching value for t+w1 (the left boundary of the window),
      wj will treat it as a null element in the window, whereas pwj will include the
      last value before t+w1 in the window.

    - If rightTable has multiple matching values for t+w1, wj will include all of
      them while pwj will only include the last row.

    The following aggregate functions in window join are optimized for better performance:

    avg, beta, count, corr, covar, first, last, max, med, min, percentile, std,
    sum, sum2, var wavg, kurtosis, prod, skew, stdp, varp, atImin, atImax, firstNot, lastNot

    .. note::

        When specifying atImax or atImin in parameter aggs of window join functions,
        if there are multiple identical extreme values in a window, the last record
        with extreme value is used for calculation by default.

    Parameters
    ----------
    leftTable : Constant
        The table to be joined.
    rightTable : Constant
        The table to be joined. It cannot be a DFS table.
    window : Constant
        A pair of integers indicating the left bound and the right bound
        (both are inclusive) of the window relative to the records in the left table.
    aggs : Constant
        A metacode or a tuple of metacode indicating one or a list of aggregate
        functions/rightTable columns. For details please refer to Metaprogramming.
        If an aggregate function is specified, its parameters must be numeric columns
        of the right table. If a rightTable column is specified, the results for
        each window will be output in the form of array vectors.
    matchingCols : Constant
        A string scalar/vector indicating matching columns.
    rightMatchingCols : Constant, optional
        A string scalar/vector indicating all the matching columns in *rightTable*,
        by default DFLT. This optional argument must be specified if at least
        one of the matching columns has different names in *leftTable* and *rightTable*.
        The joining column names in the result will be the joining column names from the left table.
    """
    ...


@builtin_function(_wls)
def wls(Y: Constant, X: Constant, W: Constant, intercept: Constant = DFLT, mode: Constant = DFLT) -> Constant:
    r"""Return the result of an weighted-least-squares regression of Y on X.

    Parameters
    ----------
    Y : Constant
        A dependent variable.
    X : Constant
        An independent variable.

        Y is a vector. X can be a matrix, table or tuple. When X is a matrix,
        if the number of rows is equal to the length of Y, each column of X is a
        factor. If the number of rows is not equal to the length of Y, but the
        number of columns is equal to the length of Y, each row of X is a factor.
    W : Constant
        A vector indicating the weight in which each element is a non-negative.
    intercept : Constant, optional
        A Boolean variable that indicates whether to include the intercept in
        regression, by default DFLT.
    mode : Constant, optional
        An integer, by default DFLT. It can be:

        - 0: a vector of the coefficient estimates

        - 1: a table with coefficient estimates, standard error, t-statistics, and p-value

        - 2: a dictionary with all statistics
    """
    ...


@builtin_function(_wma)
def wma(X: Constant, window: Constant) -> Constant:
    r"""Calculate the Weighted Moving Average (wma) for X in a sliding window of the given length.

    Parameters
    ----------
    X : Constant
        A vector/matrix/table.
    window : Constant
        A positive integer indicating the size of the sliding window.
    """
    ...


@builtin_function(_writeLog)
def writeLog(*args) -> Constant:
    r"""Write a message into the log file. It must be executed by a logged-in user.
    """
    ...


@builtin_function(_writeLogLevel)
def writeLogLevel(level: Constant, X1: Constant, *args) -> Constant:
    r"""Write logs of the specified level to the log files. It can only be called by an administrator.

    .. note::

        The specified level must be equal to or higher than the log level configured
        by the logLevel parameter or set by the setLogLevel function, otherwise the
        logs will not be written to the log file.

    Parameters
    ----------
    level : Constant
        Indicate the log level. It accepts these values in ascending order of
        importance: DEBUG (0), INFO (1), WARNING (2), and ERROR (3).
    X1 : Constant
        The content to be written to the log file. Each Xi is a line in the log file.
        The following data types are supported: Logical, Integral, Temporal, Floating,
        Literal, and Decimal.
    """
    ...


@builtin_function(_wsum)
def wsum(X: Constant, Y: Constant) -> Constant:
    r"""Return the weighted sum of squares of X and Y.

    Parameters
    ----------
    X : Constant
        A scalar, vector, matrix or table.
    Y : Constant
        A scalar, vector, matrix or table.
    """
    ...


@builtin_function(_xdb)
def xdb(host: Constant, port: Constant, userId: Constant = DFLT, password: Constant = DFLT, enableSSL: Constant = DFLT) -> Constant:
    r"""Connect to a remote site. This remote site must be on. If the connection
    is successful, it returns the handle of the remote connection.

    Parameters
    ----------
    host : Constant
        The host name (IP address or website) of the remote node.
    port : Constant
        An integral indicating the port number of the remote node
    userId : Constant, optional
        A string indicationg the user name, by default DFLT.
    password : Constant, optional
        A string indicationg the password, by default DFLT
    enableSSL : Constant, optional
        A boolean value determining whether to use the SSL protocol for encrypted communication, by default DFLT
    """
    ...


@builtin_function(_xor)
def xor(X: Constant, Y: Constant) -> Constant:
    r"""Pair each elements in X and Y to perform the "exclusive or" operation.

    Parameters
    ----------
    X : Constant
        A calar, pair, vector or matrix.
    Y : Constant
        A calar, pair, vector or matrix.
    """
    ...


@builtin_function(_year)
def year(X: Constant) -> Constant:
    r"""Return the corresponding year(s).

    Parameters
    ----------
    X : Constant
        A temporal scalar/vector.

    Returns
    -------
    Constant
        An INT scalar.
    """
    ...


@builtin_function(_yearBegin)
def yearBegin(X: Constant, startingMonth: Constant = DFLT, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""Return the first day of the year that X belongs to and that starts in the
    month of startingMonth.
    If parameter offset is specified, the result is updated every n years. The
    parameters offset and n must be specified together, and offset takes effect only when n > 1.

    Parameters
    ----------
    X : Constant
        A scalar/vector of data type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    endingMonth : Constant, optional
        An integer between 1 and 12 indicating a month, by default DFLT.
    offset : Constant, optional
        A scalar of the same data type as X, by default DFLT. It must be no greater
        than the minimum value of X.
    n : Constant, optional
        A positive integer, by default DFLT
    """
    ...


@builtin_function(_yearEnd)
def yearEnd(X: Constant, endingMonth: Constant = DFLT, offset: Constant = DFLT, n: Constant = DFLT) -> Constant:
    r"""Return the last day of the year that X belongs to and that ends in the month of endingMonth.
    If parameter offset is specified, the result is updated every n years.
    The parameters offset and n must be specified together, and offset takes effect only when n > 1.

    Parameters
    ----------
    X : Constant
        A scalar/vector of data type DATE, DATEHOUR, DATETIME, TIMESTAMP or NANOTIMESTAMP.
    endingMonth : Constant, optional
        An integer between 1 and 12 indicating a month, by default DFLT.
    offset : Constant, optional
        A scalar of the same data type as X, by default DFLT. It must be no greater
        than the minimum value of X.
    n : Constant, optional
        A positive integer, by default DFLT
    """
    ...


@builtin_function(_zTest)
def zTest(X: Constant, Y: Constant = DFLT, mu: Constant = DFLT, sigmaX: Constant = DFLT, sigmaY: Constant = DFLT, confLevel: Constant = DFLT) -> Constant:
    r"""If Y is not specified, conduct a one-sample Z-test on X. If Y is specified,
    conduct a paired-sample Z-test on X and Y.

    Parameters
    ----------
    X : Constant
        A numeric vector indicating the sample for the Z-test.
    Y : Constant, optional
        A numeric vector indicating the second sample for a paired-sample Z-test, by default DFLT
    mu : Constant, optional
        A  floating number, by default DFLT. If Y is not specified, mu is the mean
        value of X in the null hypothesis; if Y is specified, mu is the difference
        in the mean values of X and Y in the null hypothesis. It is optional and the default value is 0.
    sigmaX : Constant, optional
        A floating number indicating the standard deviation of X, by default DFLT.
    sigmaY : Constant, optional
        A floating number indicating the standard deviation of Y, by default DFLT.
    confLevel : Constant, optional
        A floating number between 0 and 1 indicating the confidence level of the test, by default DFLT.

    Returns
    -------
    Constant
        A dictionary with the following keys:

        - stat: a table with p-value and confidence interval under 3 alternative hypotheses.

        - confLevel: confidence level

        - method: "One sample Z-test" if Y is not specified; "Two sample Z-test" if Y is specified.

        - zValue: Z-stat
    """
    ...


@builtin_function(_zigzag)
def zigzag(HL: Constant, change: Constant = DFLT, percent: Constant = DFLT, retrace: Constant = DFLT, lastExtreme: Constant = DFLT) -> Constant:
    r"""zigzag is mainly used to filter values with smaller movements in HL. Only
    extreme points that satisfy the conditions will be output.
    If HL is a vector, return a vector with the same length as HL; if HL is a matrix,
    return a vector with the same number of rows as HL.

    Parameters
    ----------
    HL : Constant
        A numeric vector or a numeric matrix with two columns.
    change : Constant, optional
        The minimum threshold for extreme value movement, by default DFLT
    percent : Constant, optional
        A Boolean value indicating whether change is used as a percentage, by default DFLT
    retrace : Constant, optional
        A Boolean value, by default DFLT

        - true: change represents a retracement of the previous move.

        - false: change represents the change between the extreme points.
    lastExtreme : Constant, optional
        A Boolean value indicating whether to output the last point if multiple
        consecutive points have the same value, by default DFLT.
    """
    ...


@builtin_function(_zscore)
def zscore(X: Constant) -> Constant:
    r"""If X is a vector, return the zscore for all elements of X.
    If X is a matrix, the zscore calculation is conducted within each column of X.
    As with all aggregate functions, null values are not included in the calculation.

    Parameters
    ----------
    X : Constant
        A vector/matrix
    """
    ...
