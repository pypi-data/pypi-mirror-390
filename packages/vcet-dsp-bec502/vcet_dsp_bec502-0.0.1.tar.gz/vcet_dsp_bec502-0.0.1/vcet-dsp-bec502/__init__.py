from operator import mod
import cmath as cm
import math as m
def lin_conv(x,h):
    N=len(x)+len(h)-1
    x= x+ [0]*(N-len(x))
    h= h+ [0]*(N-len(h))
    y=[0]*N 
    for n in range(N):
        for k in range(n+1):
            y[n]+=x[k]*h[n-k]
    return y 
def circ_conv(x,h):
    N=len(x)
    y=[0]*N 
    for n in range(N):
        for k in range(N):
            y[n]+=x[k]*h[mod((n-k),N)]
    return y
def dft(x):
    N=len(x)
    X=[0]*N
    for k in range(N):
        for n in range(N):
            X[k]+=x[n]*cm.exp(-1j*2*m.pi*k*n/N)
    return X
def idft(X):
    N=len(X)
    x=[0]*N
    for n in range(N):
        for k in range(N):
            x[n]+=X[k]*cm.exp(1j*2*m.pi*k*n/N)
        x[n]/=N
    return x
def fir_lp(N,wc):
    alpha=(N-1)/2
    wh=[0]*N
    hd=[0]*N
    h=[0]*N
    for n in range(N):
        if n==alpha:
            hd[n]=wc/m.pi 
            wh[n]=1
            h[n]=hd[n]*wh[n]
        else:
            hd[n]=m.sin(wc*(n-alpha))/(m.pi*(n-alpha))
            wh[n]=0.54-0.46*m.cos((2*m.pi*n)/(N-1))
            h[n]=hd[n]*wh[n]
    return h
def fir_hp(N,wc):
    alpha=(N-1)/2
    wh=[0]*N
    hd=[0]*N
    h=[0]*N
    for n in range(N):
        if n==alpha:
            hd[n]=(1/m.pi)*(m.pi-wc) 
            wh[n]=1
            h[n]=hd[n]*wh[n]
        else:
            hd[n]=-m.sin(wc*(n-alpha))/(m.pi*(n-alpha))
            wh[n]=0.54-0.46*m.cos((2*m.pi*n)/(N-1))
            h[n]=hd[n]*wh[n]
    return h
def dtft(h):
    N=len(h)
    w=[((i*0.01)-m.pi) for i in range(629)]
    H=[0]*len(w)
    Hm=[0]*len(w)
    omega=-m.pi
    for w1 in range(len(w)):
        for n in range(N):
            H[w1]+=h[n]*cm.exp(-1j*omega*n)
        Hm[w1]=abs(H[w1])
        omega+=0.01
    return w,Hm
def dfs(xn,Nc,N):
    Xk=[0]*N
    for k in range(Nc):
        for n in range(N):
            Xk[k]+=xn[n]*cm.exp(-1j*2*m.pi*k*n/N)
        Xk[k]=Xk[k]/N
    return Xk
def idfs(Xk,Nc,N):
    xrec=[0]*N
    for n in range(N):
        for k in range(Nc):
            xrec[n]+=Xk[k]*cm.exp(1j*2*m.pi*k*n/N)
    return xrec 
def dct(x):
    N=len(x)
    X=[0]*N
    for k in range(N):
        for n in range(N):
            X[k]=X[k]+ (m.cos(((m.pi*(2*n+1)*k)/(2*N)))*x[n])
        if k==0:
            X[k]=(1/N)**(0.5)*X[k]
        else:
            X[k]=(2/N)**(0.5)*X[k]
    return X
def dwt(x,Lo_D,Hi_D):
    lp=lin_conv(x,Lo_D)
    hp=lin_conv(x,Hi_D)
    ca=[lp[i] for i in range(1,len(lp),2)]
    cd=[hp[i] for i in range(1,len(hp),2)]
    return ca,cd
def diff_eqn(b,a,x):
    N=len(x)
    a1=[0]*(N)
    b1=[0]*(N)
    y=[0]*(N)
    if(len(a)==1):
        for i in range(len(b)):
            b1[i]=b[i]
        for n in range(N):
            for k in range(n+1):
                y[n]=y[n]+b1[k]*x[n-k]
        return y
    else:
        for i in range(len(a)):
            a1[i]=a[i]
        for i in range(len(b)):
            b1[i]=b[i]
        for n in range(N):
            term1=0
            term2=0
            for k in range(n+1):
                term1=term1-a1[k]*y[n-k]
                term2=term2+b1[k]*x[n-k]
                y[n]=term1+term2
    return y
def overlap_save(x,h,N):
    sx=len(x)
    M=len(h)
    L=N-M+1
    h=list(h)+[0]*(L-1)
    [q,r]=divmod(len(x),L)
    if r==0:
        nof=q+1
    else:
        x=list(x)+[0]*(L-r)
        nof=q+2
    xseg = [[0] * L for _ in range(nof)]
    xseg1 = [[0] * N for _ in range(nof)]
    yseg1 = [[0] * N for _ in range(nof)]
    for i in range(nof-1):
        xseg[i] = x[i * L : i * L + L]
    for i in range(nof):
        for j in range(L):
            if i==0:
                xseg1[i][j+(M-1)]=xseg[i][j]
            else:
                xseg1[i][j+(M-1)]=xseg[i][j]
                xseg1[i][0:M-1]=xseg[i-1][L-M+1:L]
    print(f'Segmented inputs={xseg1}')
    for i in range(nof):
        yseg1[i]=circ_conv(xseg1[i], h)
    print(f'Segmented outputs={yseg1}')
    yseg2 = [[0] * L for _ in range(nof)]
    for i in range(nof):
        for j in range(L):
            yseg2[i][j] = yseg1[i][j + (M - 1)]
    y1 = []
    for row in yseg2:
        y1.extend(row)
    
    y1 = y1[0:sx + M - 1]
    print(f'Final sequence using Overlap save method={y1}') 
def overlap_add(x, h, N):
    sx = len(x)
    M = len(h)
    L = N - M + 1
    h = list(h) + [0] * (L - 1)
    q, r = divmod(len(x), L)
    nof = q + 1
    # Initialize arrays using nested lists
    xseg = [[0] * L for _ in range(nof)]
    xseg1 = [[0] * N for _ in range(nof)]
    yseg1 = [[0] * N for _ in range(nof)]
    yseg3 = [[0] * N for _ in range(nof)]
    yseg2 = [[0] * L for _ in range(nof)]
    # Fill xseg with segments of x
    for i in range(nof - 1):
        xseg[i] = x[i * L : i * L + L]
    # Handle the last segment
    xseg[nof - 1] = [0] * L  # Initialize with zeros
    for j in range(r):
        xseg[nof - 1][j] = x[len(x) - r + j]
    # Copy xseg to xseg1 (first L elements)
    for i in range(nof):
        for j in range(L):
            xseg1[i][j] = xseg[i][j]
    print(f'Segmented inputs={xseg1}')
    # Perform circular convolution for each segment
    for i in range(nof):
        yseg1[i] = circ_conv(xseg1[i], h)
    # Copy yseg1 to yseg3
    for i in range(nof):
        for j in range(N):
            yseg3[i][j] = yseg1[i][j]
    # Overlap-add operation
    for i in range(nof - 1):
        for j in range(M - 1):
            yseg1[i + 1][j] = yseg1[i][N - (M - 1) + j] + yseg1[i + 1][j]
    print(f'Segmented outputs={yseg1}')
    # Extract first L elements from each segment
    for i in range(nof):
        for j in range(L):
            yseg2[i][j] = yseg1[i][j]
    # Flatten yseg1 and yseg2
    yseg1_flat = []
    for row in yseg1:
        yseg1_flat.extend(row)
    y1_flat = []
    for row in yseg2:
        y1_flat.extend(row)
    # Combine results
    y1 = y1_flat + yseg1_flat[-(M - 1):]
    y1 = y1[0:sx + M - 1]
    print(f'Final sequence using Overlap add method={y1}')      
def radix2_dit_fft(x, stage=0):
    """
    Compute the DFT of x using Radix-2 DIT FFT algorithm
    showing only intermediate and final stage outputs.
    """
    N = len(x)
    
    # Display stage output
    if stage == 0:
        print(f"\nINITIAL STAGE (N={N}):")
        print(f"Input: {format_complex_list(x)}")
    else:
        print(f"\nSTAGE {stage} (N={N}):")
        print(f"Input: {format_complex_list(x)}")
    
    # Base case
    if N == 1:
        print(f"Output: {format_complex_list(x)}")
        return x
    
    # Recursive calls
    even = radix2_dit_fft(x[0::2], stage + 1)
    odd = radix2_dit_fft(x[1::2], stage + 1)
    
    # Combine results
    X = [0] * N
    for k in range(N // 2):
        twiddle = cm.exp(-2j * cm.pi * k / N)
        X[k] = even[k] + twiddle * odd[k]
        X[k + N // 2] = even[k] - twiddle * odd[k]
    
    print(f"Output: {format_complex_list(X)}")
    
    return X
def radix2_dif_fft(x, stage=0):
    """
    Compute the DFT of x using Radix-2 Decimation-in-Frequency FFT algorithm
    showing intermediate and final stage outputs.
    """
    N = len(x)
    
    # Display current stage
    if stage == 0:
        print(f"\nINITIAL STAGE (N={N}):")
        print(f"Input: {format_complex_list(x)}")
    else:
        print(f"\nSTAGE {stage} (N={N}):")
        print(f"Input: {format_complex_list(x)}")
    
    # Base case
    if N == 1:
        print(f"Output: {format_complex_list(x)}")
        return x
    
    # DIF: Split into first half and second half with butterfly operations
    first_half = [0] * (N // 2)
    second_half = [0] * (N // 2)
    
    print("Butterfly operations:")
    for k in range(N // 2):
        # Butterfly operation: 
        # first_half[k] = x[k] + x[k + N//2]
        # second_half[k] = (x[k] - x[k + N//2]) * W_N^k
        
        twiddle = cm.exp(-2j * cm.pi * k / N)
        
        first_half[k] = x[k] + x[k + N//2]
        second_half[k] = (x[k] - x[k + N//2]) * twiddle
        
        print(f"  k={k}:")
        print(f"    First[{k}] = x[{k}] + x[{k + N//2}] = {format_complex(x[k])} + {format_complex(x[k + N//2])} = {format_complex(first_half[k])}")
        print(f"    Second[{k}] = (x[{k}] - x[{k + N//2}]) × W_{N}^{k} = ({format_complex(x[k])} - {format_complex(x[k + N//2])}) × {format_complex(twiddle)} = {format_complex(second_half[k])}")
    
    print(f"First half after butterflies: {format_complex_list(first_half)}")
    print(f"Second half after butterflies: {format_complex_list(second_half)}")
    
    # Recursive calls on both halves
    print(f"\nRecursing into first half (N={N//2}):")
    first_half_fft = radix2_dif_fft(first_half, stage + 1)
    
    print(f"\nRecursing into second half (N={N//2}):")
    second_half_fft = radix2_dif_fft(second_half, stage + 1)
    
    # Combine results (first half gives even indices, second half gives odd indices)
    X = [0] * N
    for k in range(N // 2):
        X[2 * k] = first_half_fft[k]      # Even indices
        X[2 * k + 1] = second_half_fft[k] # Odd indices
    
    print(f"STAGE {stage} Output (N={N}):")
    print(f"Combined result: {format_complex_list(X)}")
    return X
def format_complex_list(c_list):
    """Format a list of complex numbers for clean display"""
    return [format_complex(c) for c in c_list]

def format_complex(c):
    """Format single complex number"""
    real = round(c.real, 4)
    imag = round(c.imag, 4)
    if abs(real) < 1e-10: real = 0
    if abs(imag) < 1e-10: imag = 0
    if imag == 0:
        return f"{real:7.4f}"
    elif real == 0:
        return f"{imag:7.4f}j"
    else:
        sign = "+" if imag >= 0 else ""
        return f"{real:7.4f}{sign}{imag:7.4f}j"
