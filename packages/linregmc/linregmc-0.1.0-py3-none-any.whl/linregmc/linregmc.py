import numpy as np
from numpy.matlib import repmat,randn
import logging

def addnoise(yinp,ysiginp,nmc=10000,distrib='normal'):	
	"""Adds noise to an array of data points (or a single value).
	
	Creates a matrix of nmc vectors with the mean values of y but with
	added random noise of standard deviation ysig. 
	You might want to initialize the random number generator in forehand.
	
	
	Parameters
	----------
	y : array
	    data vector
	ysig : array
	    standard deviation vector (same length as y, or a single value)
	nmc : int, default 10000
	    number of Monte Carlo copies
	distrib : str, default 'normal'
	    'norm'/'normal' gives normal distribution
	    'lognorm'/'lognormal' give lognormal distribution (useful for example if negative results are unphysical)
	
	Returns
	-------
	array
		the data vector with added noise
		(always two-dimensional, but only one column if y was a single value)
	
	Examples
	--------
	>>> y = np.array([1.2, 2.3, 3.7])
	>>> ysig = np.array([0.1, 0.3, 0.2])
	>>> y1 = addnoise(y, ysig)  # different stdev for the three points, normal distribution
	>>> y1.shape  # (10000, 3)
	>>> y2 = addnoise(y, 0.2, 1000, distrib='lognorm')   # same stdev for the three points, lognormal distribution
	>>> y2.shape  # (1000, 3)
	>>> y3 = addnoise(1.5, 0.2) # only one point
	>>> y3.shape  # (10000, 1)   
	"""
	
	
	yinp = np.asarray(yinp)
	ysiginp = np.asarray(ysiginp)
	if np.ndim(yinp)>1 or np.ndim(ysiginp)>1:
		raise Exception('y and ysig must not have higher dimension than 1.')
	if np.size(ysiginp) == 1:
		ysiginp = ysiginp*np.ones(np.size(yinp))  #If ysiginp is a scalar, turn it into a vector with identical elements
	if np.size(yinp) != np.size(ysiginp):
		raise Exception('y and ysig must have the same length.')

	n=np.size(yinp)
	y=yinp.reshape((1,n))
	ysig=ysiginp.reshape((1,n))
	if distrib.lower() in ('norm' ,'normal'):
		
		return np.array(repmat(y,nmc,1)) + np.array(repmat(ysig,nmc,1))*np.array(randn(nmc,n))
	elif  distrib.lower() in ('lognorm','lognormal'):
			mu = np.log(y**2/np.sqrt(ysig**2+y**2))  # mu of lognormal dist
			sigma = np.sqrt(np.log(ysig**2/y**2+1))  # sigma of lognormal dist
			return np.exp(np.array(randn(nmc,n))*np.array(repmat(sigma,nmc,1)) + np.array(repmat(mu,nmc,1)))
	else:
		raise Exception('Distribution named "' + distrib + '" is not recognized.')



def linreg(xinp, yinp, ndeg=1, fitfunc = None, weighted=True, plot = False):
	"""Performs linear fitting ax+b=y with error analysis using a Monte Carlo approach.
	
	Parameters
	----------
	xinp : array
	    an NM x N matrix: the NX data sets of x values (N data points)
	yinp : array
	    an NY x N matrix: the NY data sets of y values (N data points)
		NX and NY need not be the same. In particular one may use a
		single data set (without added noise) for one of them.
		The number of fits equals NM = max(NX,NY) and if there are less data
		sets for one of x or y, they are just cyclically reused.
	ndeg : int, default 1
		the degree of the polynomial used for fitting
	fitfunc : list, optional
		a list of functions of x that are used as basis functions instead of a polonymial
		(ndeg and fitfunc cannot both be specified)
	weighted: boolean, default True
		weight the importance of each data point by 1/stdev (recommended)
	plot : boolean, default False
	    an optional argument that specifies whether to plot the chi2 distribution
	    to visualize the "goodness-of-fit".
	
	Returns
	-------
	pp  : array (ndeg+1 elements)
		single-fit value of each parameter (can be used as the result)
	psig  : array (ndeg+1 elements)
		standard deviation of each parameter
	pchi2 : float
		goodness-of-fit, i.e. probability of chi>chi0
		Note: not well-defined
	pmc  : array
		a (NM x (ndeg+1) matrix, the fitted parameters for all data sets
		
	Examples
	--------
	>>> x = np.array([0.1, 0.2, 0.3])
	>>> y = np.array([1.2, 2.3, 3.7])
	>>> y_mc=addnoise(y, 0.1)
	>>> pp,psig,pchi2,pmc = linreg(x, y_mc)	
	>>> print(pp)   #[12.517 -0.102]
	>>> print(pmc.shape)   # (10000, 2)	
	>>> pp,psig,pchi2,pmc = linreg(x, y_mc, fitfunc=[lambda x: np.exp(x), lambda x: 1]) #Fit to y=ae^x+b instead	
	"""

	if fitfunc != None and ndeg==1:  #Assume that ndeg was not specified, there is no way to know...
		ndeg = len(fitfunc)-1
	elif fitfunc != None and ndeg!=1: 
		raise Exception('Only one of ndeg and fitfunc can be specified.')
	if np.ndim(xinp) == 1:
		x=xinp.reshape((1,np.size(xinp)))
	else:
		x= xinp
	if np.ndim(yinp) == 1:
		y=yinp.reshape((1,np.size(yinp)))
	else:
		y=yinp
	if np.size(x,1) != np.size(y,1):
		raise Exception('Number of columns in x and y must be equal')
	N=np.size(x,1)
	xn=np.size(x,0)
	yn=np.size(y,0)


	def buildmat(xx,ss=1.0):
		if fitfunc==None:
			return np.stack([xx**k/ss for k in range(ndeg,0,-1)]+[np.ones(N)/ss], axis=1)
		else:
			return np.stack([(np.zeros(N)+func(xx))/ss for func in fitfunc], axis=1)

    
	xs=np.median(x, axis=0)
	ys=np.median(y, axis=0)   #Reproduces original data points independent of distribution
	if weighted:
		deltax=np.std(xs)/(N*100)   #gives deltax with correct order of magnitude
		pnow=np.linalg.lstsq(buildmat(xs), ys, rcond=None)[0]   #parameters if no weights are used
		fprime=(np.matmul(buildmat(xs+deltax),pnow)-np.matmul(buildmat(xs-deltax),pnow))/(2*deltax)  #numerical derivative
		sig=np.sqrt(np.var(y, axis=0)+fprime**2*np.var(x, axis=0))  #Standard error propagation
		#TODO: If weighting is important, the estimation of sig should be done iteratively because fprime depends on the fit and thus on sig
		if xn==1 and yn==1:
			sig=1.0
			logging.warning('Single data sets, using unweighted fit instead')
		elif np.any(sig==0):
			sig=1.0
			logging.warning('Points with no variation encountered, using unweighted fit instead')
	else:
		sig=1.0
		
	#Perform single fit to get the base chi2 value
	Xt=buildmat(xs)
	X=buildmat(xs,sig)
	YS=ys/sig
	pp=np.linalg.lstsq(X,YS, rcond=None)[0]
	yfit=np.matmul(Xt,pp)  # y(xs) value according to model   
	chi2 = sum((YS - np.matmul(X,pp))**2)

	nmc = max(xn,yn)
	pmc = np.zeros((nmc,ndeg+1)) 
	chi2mc = np.zeros(nmc)
	for i in range(nmc):
		X=buildmat(x[i%xn,:],sig)
		Y=(yfit+y[i%yn,:]-ys)/sig   
		p=np.linalg.lstsq(X,Y, rcond=None)[0] 
		pmc[i,:]=p
		chi2mc[i] = sum((Y - np.matmul(X,p))**2)

	psig = np.std(pmc,0)
	pmean = np.mean(pmc,0) #Not used
	pchi2=sum(chi2mc>chi2)/nmc     #Percentage of MC samples having greater chi2 than the observation
	
	if plot:
		import matplotlib.pyplot as plt
		fig, ax = plt.subplots(1, 1, figsize=(4, 2))
		counts,*_=ax.hist(chi2mc,bins=50)
		ycent=0.5*max(counts)
		ax.plot([chi2,chi2],[0,ycent],'r-')
		ax.set_yticks([])
		ax.set_xlabel(r"$\chi^2$")
		plt.show()
		
	return (pp,psig,pchi2,pmc)



def confidence(X, level=0.683, plot=False):
	"""Statistical analysis of the data in matrix X.
	
	It is assumed that the number of data points are large; all properties
	are calculated from the data itself.
	
	Parameters
	----------
	X : array
	    data matrix. Data in columns. For example, if X contains data
	    from two measurements, data for measurement 1 is in column 1
	    and measurement 2 in columns 2.
	    If only one column, a 1d-array is also acceptable
	level : float, default 0.683
	    desired confidence level
	plot : boolean, default False
	    an optional boolean specifying whether to plot histograms for each column
	    where a general statistic is shown as a red errorbar (median +/- stdev)
	    and the confidence intervals are shown with black lines.
	    The red markers at the bottom show the simpler (median +/- err) 
	    interval which should normally coincide with the confidence interval
	    unless the distribution is skew (in which case the confidence interval is more reliable).
	    If X has exactly two columns, a scatter plot showing possible correlation between
	    the two columns is also produced.
	
	Returns
	-------
	err : float
	    estimated error in the columns based on selected confidence level.
	confint : list
	    a list of tuples (low, high), the confidence interval for each input column
	    (pconf*100% of values are found within this interval around median) 
	    If the input x was a 1d-array, a single tuple is returned instead of a list

	Examples
	--------
	>>> x = np.array([0.1, 0.2, 0.3])
	>>> y = np.array([1.2, 2.3, 3.7])
	>>> y_mc=addnoise(y, 0.1)
	>>> pp,psig,pchi2,pmc = linreg(x, y_mc)
	>>> err,confint = confidence(pmc, 0.95)
	>>> print(err)    # gives [1.364 0.296]
	>>> print(confint)    # gives [(11.16, 13.88), (-0.401, 0.190)]
	
	"""

	onedim = (np.ndim(X) == 1)
	
	if onedim:  #convert to matrix, then convert back to onedim at the end
		X=X.reshape((np.size(X),1))
	
	if level <= 0 or level >= 1:
		raise Exception("levvel must be 0 < level < 1.")
	
	if np.size(X,1) > np.size(X,0):
		print("Warning. It appears that your data is not placed column-wise.")
	
	N = np.size(X,0) #number of data points
	n = np.size(X,1)  #number of dimensions (columns)
	
	# GUM recommendation. ncut is the complement to pconf, ie the 1-pconf
	# fraction of points.
	#ncut = floor((N - floor(level*N+0.5) + 1)/2);   
	
	median = np.median(X,0)
	sig = np.std(X,0)
	absdiff = abs(X-np.mean(X,0)) #Absolute difference to mean value
	plow = np.zeros(n)
	phigh = np.zeros(n)
	err = np.zeros(n)
	for j in range(n):
		tmp=np.sort(X[:,j])
		plow[j]=tmp[round(max(1,0.5*(1-level)*N))-1]
		phigh[j]=tmp[round(min(N,1-0.5*(1-level)*N))-1]
		tmp=np.sort(absdiff[:,j])
		err[j]=tmp[round(min(N,level*N))-1]
	
	if plot:
		import matplotlib.pyplot as plt
		import matplotlib.gridspec as gridspec
		nvar=np.size(X,1)
		if nvar==2: #Exactly two parameters so produce a scatter plot and histograms
			fig = plt.figure(figsize=(8, 4.8))
			gs = gridspec.GridSpec(2, 2, width_ratios=[1.5, 1], height_ratios=[1, 1])
			# Left square spans both rows
			ax_left = fig.add_subplot(gs[:, 0])
			axes = [fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 1])]
			ax_left.set_aspect('equal')
			ax_left.scatter(X[:,0],X[:,1],s=0.1)
			ax_left.set_xlabel('a')
			ax_left.set_ylabel('b')
			ax_left.plot([plow[0],plow[0]],[np.min(X[:,1]),np.max(X[:,1])],'k--')
			ax_left.plot([phigh[0],phigh[0]],[np.min(X[:,1]),np.max(X[:,1])],'k--')
			ax_left.plot([np.min(X[:,0]),np.max(X[:,0])],[plow[1],plow[1]], 'k--')
			ax_left.plot([np.min(X[:,0]),np.max(X[:,0])],[phigh[1],phigh[1]], 'k--')
			
			ax_left.set_aspect(1.0/ax_left.get_data_ratio(), adjustable='box')
		else:  #only produce histograms
			fig, axes = plt.subplots(nrows=nvar, ncols=1, figsize=(4, 2*nvar))
			if nvar==1: axes=[axes] # fix stupid inconsistency in plt.subplots so that axes is always a list
		
		for i,ax in enumerate(axes):
			counts,*_=ax.hist(X[:,i], bins=50)
			ycent=0.5*max(counts)
			ax.errorbar(median[i],ycent,xerr=sig[i],fmt='ro',capsize=5)
			ax.plot([plow[i],plow[i]]  ,[0,0.8*ycent],'k--')
			ax.plot([phigh[i],phigh[i]],[0,0.8*ycent],'k--')
			ax.plot([median[i]-err[i], median[i]-err[i]], [0,0.1*ycent],'r-')
			ax.plot([median[i]+err[i], median[i]+err[i]], [0,0.1*ycent],'r-')
			ax.set_xlabel(chr(ord('a')+i))  #Name the variables a,b,c...
			ax.set_yticks([])
	
		plt.tight_layout()
		plt.show()
	
	if onedim:
		return (err[0], (plow[0], phigh[0])) #simply return scalars
	else:
		return (err, list(zip(plow, phigh)))


def linconf(xinp, yinp, ysig, nmc=10000, distrib='normal', level=0.683, ytransform=None, restransform=None):
	"""Performs the full Monte Carlo linear regression with confidence calculation.
	
	This is done by applying the following 5 steps in succession:
	- addnoise to y values
	- transform y values (skipped if ytransform==None)
	- linreg (x,y)
	- calculate a tuple of results from a,b   (skipped if restransform==None)
	- confidence for each result
	
	For detailed description of parameters, see previous functions
	Returns (reslist, pchi2) where reslist is a list of (result, error, confidenceinterval) for each calculated result
	"""
	
	ymc=addnoise(yinp, ysig, nmc, distrib)
	if ytransform!=None:
		ymc = ytransform(ymc)
	pp,psig,pchi2,pmc=linreg(xinp,ymc)
	if restransform!=None:
		results=restransform(pp[0],pp[1])
		results_mc=restransform(pmc[:,0],pmc[:,1])
	else:
		results=(pp[0],pp[1])
		results_mc=(pmc[:,0],pmc[:,1])
	rlist=[]
	for r,rmc in zip(results,results_mc):
		perr,confint=confidence(rmc, level)
		rlist.append((r,perr,confint))
	return (rlist,pchi2)
