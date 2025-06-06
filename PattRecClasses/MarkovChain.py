import numpy as np
from .DiscreteD import DiscreteD

class MarkovChain:
    """
    MarkovChain - class for first-order discrete Markov chain,
    representing discrete random sequence of integer "state" numbers.
    
    A Markov state sequence S(t), t=1..T
    is determined by fixed initial probabilities P[S(1)=j], and
    fixed transition probabilities P[S(t) | S(t-1)]
    
    A Markov chain with FINITE duration has a special END state,
    coded as nStates+1.
    The sequence generation stops at S(T), if S(T+1)=(nStates+1)
    """
    def __init__(self, initial_prob, transition_prob):

        self.q = initial_prob  #InitialProb(i)= P[S(1) = i]
        self.A = transition_prob #TransitionProb(i,j)= P[S(t)=j | S(t-1)=i]

        self.nStates = transition_prob.shape[0]

        self.is_finite = False
        if self.A.shape[0] != self.A.shape[1]:
            self.is_finite = True


    def probDuration(self, tmax):
        """
        Probability mass of durations t=1...tMax, for a Markov Chain.
        Meaningful result only for finite-duration Markov Chain,
        as pD(:)== 0 for infinite-duration Markov Chain.
        
        Ref: Arne Leijon (201x) Pattern Recognition, KTH-SIP, Problem 4.8.
        """
        pD = np.zeros(tmax)

        if self.is_finite:
            pSt = (np.eye(self.nStates)-self.A.T)@self.q

            for t in range(tmax):
                pD[t] = np.sum(pSt)
                pSt = self.A.T@pSt

        return pD

    def probStateDuration(self, tmax):
        """
        Probability mass of state durations P[D=t], for t=1...tMax
        Ref: Arne Leijon (201x) Pattern Recognition, KTH-SIP, Problem 4.7.
        """
        t = np.arange(tmax).reshape(1, -1)
        aii = np.diag(self.A).reshape(-1, 1)
        
        logpD = np.log(aii)*t+ np.log(1-aii)
        pD = np.exp(logpD)

        return pD

    def meanStateDuration(self):
        """
        Expected value of number of time samples spent in each state
        """
        return 1/(1-np.diag(self.A))
    
    def rand(self, tmax):
        """
        S=rand(self, tmax) returns a random state sequence from given MarkovChain object.
        
        Input:
        tmax= scalar defining maximum length of desired state sequence.
           An infinite-duration MarkovChain always generates sequence of length=tmax
           A finite-duration MarkovChain may return shorter sequence,
           if END state was reached before tmax samples.
        
        Result:
        S= integer row vector with random state sequence,
           NOT INCLUDING the END state,
           even if encountered within tmax samples
        If mc has INFINITE duration,
           length(S) == tmax
        If mc has FINITE duration,
           length(S) <= tmaxs
        """
        
        S = []
        initial_dist = DiscreteD(self.q)
        current_state = initial_dist.rand(1)[0]
        
        if self.is_finite and current_state == self.nStates + 1:
            return np.array([], dtype=int) 
        
        S.append(current_state)
        
        for _ in range(1, tmax):
            trans_probs = self.A[current_state - 1, :]
            
            trans_dist = DiscreteD(trans_probs)
            next_state = trans_dist.rand(1)[0]
            
            if self.is_finite and next_state == self.nStates + 1:
                break 
            
            S.append(next_state)
            current_state = next_state
        
        return np.array(S, dtype=int)

    def viterbi(self):
        pass
    
    def stationaryProb(self):
        pass
    
    def stateEntropyRate(self):
        pass
    
    def setStationary(self):
        pass

    def logprob(self):
        pass

    def join(self):
        pass

    def initLeftRight(self):
        pass
    
    def initErgodic(self):
        pass

    def forward(self, pX):
        """
        Scaled forward algorithm.
        pX: sequence of observations, length T
        returns: alpha_hat (nStates×T), c (T,) scale factors
        """
        N = self.nStates
        T = len(pX)

        alpha_hat = np.zeros((N, T))
        c = np.zeros(T)

        # t = 0 initialization
        b0 = np.array([self.B[j].prob(pX[0]) for j in range(N)])
        alpha_hat[:, 0] = self.q * b0
        c[0] = 1.0 / alpha_hat[:, 0].sum()
        alpha_hat[:, 0] *= c[0]

        # recursion
        for t in range(1, T):
            bt = np.array([self.B[j].prob(pX[t]) for j in range(N)])
            alpha_hat[:, t] = (alpha_hat[:, t-1] @ self.A) * bt
            c[t] = 1.0 / alpha_hat[:, t].sum()
            alpha_hat[:, t] *= c[t]

        return alpha_hat, c

    def finiteDuration(self):
        pass
    
    def backward(self, c, pX):
        """
        Scaled backward algorithm.
        c: the scale factors returned by forward()
        pX: same observation sequence
        returns beta_hat (nStates×T)
        """
        N = self.nStates
        T = len(pX)

        beta_hat = np.zeros((N, T))

        # initialize at t = T−1
        beta_hat[:, T-1] = c[T-1]

        # recursion backward
        for t in range(T-2, -1, -1):
            bt1 = np.array([self.B[j].prob(pX[t+1]) for j in range(N)])
            beta_hat[:, t] = c[t] * (self.A * bt1).dot(beta_hat[:, t+1])

        return beta_hat

    def adaptStart(self):
        pass

    def adaptSet(self):
        pass

    def adaptAccum(self):
        pass
