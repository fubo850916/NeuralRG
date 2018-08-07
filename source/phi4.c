#include<stdio.h>
#include<stdlib.h>
#include<math.h>

void hoppingTable(int nvars,int dims,int L, int hopping[nvars][dims*2])
{
    int y,LK;
    int xk,k,dxk;
    for(int i=0;i<nvars;i++)
    {
        LK = nvars;
        y = i;
        for(k = dims-1;k>=0;k--)
        {
            LK/=L;
            xk = y/LK;
            y = y-xk*LK;
            if(xk<L-1)
            dxk = LK;
            else
            dxk = LK*(1-L);
            hopping[i][k] = i+dxk;

            if(xk>0)
            dxk = -LK;
            else
            dxk = LK*(L-1);
            hopping[i][k+dims] = i+dxk;
        }
    }
}


double phi4action(int nvars, int dims, double kappa, double lambda, double *config, int hopping[nvars][dims*2])
{
    double S = 0;
    double phi2;
    double tmp=0;
    int j;
    for(int i =0;i<nvars;i++)
    {
        tmp = 0;
        for(j=0;j<dims;j++)
        {
            tmp += config[(hopping[i][j])];
        }
        phi2 = config[i]*config[i];
        S += -2*kappa*tmp*config[i] + phi2+lambda*(phi2-1.0)*(phi2-1.0);
    }
    return S;

}

int main(void)
{
    int dims = 2;
    int l = 8;
    int nvars;
    nvars = pow(l,dims);
    int hopT[nvars][2*dims];
    hoppingTable(nvars,dims,l,hopT);
    double kappa = 0.15;
    double lambda = 1.145;

    double configure[nvars];
    for(int i = 0;i<nvars;i++)
    {
        configure[i] = i;
    }

    printf("%f",phi4action(nvars,dims,kappa,lambda,configure,hopT));

    return 0;
}

