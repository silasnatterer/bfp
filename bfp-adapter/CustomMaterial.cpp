#include "CustomMaterial.h"

BEGIN_FECORE_CLASS(CustomMaterial, FEUncoupledMaterial)
	ADD_PARAMETER(m_c1, "c1");
	ADD_PARAMETER(m_c2, "c2");
END_FECORE_CLASS();


CustomMaterial::CustomMaterial(FEModel *pfem) : FEUncoupledMaterial(pfem)
{}

bool CustomMaterial::Init()
{
    if (FEUncoupledMaterial::Init() == false) return false;
    
    // Do additional initialization here
    
    return true;
}

bool CustomMaterial::Validate()
{
    if (FEUncoupledMaterial::Validate() == false) return false;
    
    // Do additional parameter validation here
    
    return true;
}

mat3ds CustomMaterial::DevStress(FEMaterialPoint& mp)
{
    FEElasticMaterialPoint& pt = *mp.ExtractData<FEElasticMaterialPoint>();

	// get material parameters
	double c1 = m_c1;
	double c2 = m_c2;

	// determinant of deformation gradient
	double J = pt.m_J;

	// calculate deviatoric left Cauchy-Green tensor
	mat3ds B = pt.DevLeftCauchyGreen();

	// calculate square of B
	mat3ds B2 = B.sqr();

	// Invariants of B (= invariants of C)
	// Note that these are the invariants of Btilde, not of B!
	double I1 = B.tr();
	double I2 = 0.5*(I1*I1 - B2.tr());

	// --- TODO: put strain energy derivatives here ---
	//
	// W = C1*(I1 - 3) + C2*(I2 - 3)
	//
	// Wi = dW/dIi
	double W1 = c1;
	double W2 = c2;
	// ---

	// calculate T = F*dW/dC*Ft
	// T = F*dW/dC*Ft
	mat3ds T = B*(W1 + W2*I1) - B2*W2;
    
	return T.dev()*(2.0/J);
 }

tens4ds CustomMaterial::DevTangent(FEMaterialPoint& mp)
{
    FEElasticMaterialPoint& pt = *mp.ExtractData<FEElasticMaterialPoint>();

	// get material parameters
	double c1 = m_c1;
	double c2 = m_c2;

	// determinant of deformation gradient
	double J = pt.m_J;
	double Ji = 1.0/J;

	// calculate deviatoric left Cauchy-Green tensor: B = F*Ft
	mat3ds B = pt.DevLeftCauchyGreen();

	// calculate square of B
	mat3ds B2 = B.sqr();

	// Invariants of B (= invariants of C)
	double I1 = B.tr();
	double I2 = 0.5*(I1*I1 - B2.tr());

	// --- TODO: put strain energy derivatives here ---
	// Wi = dW/dIi
	double W1, W2;
	W1 = c1;
	W2 = c2;
	// ---

	// calculate dWdC:C
	double WC = W1*I1 + 2*W2*I2;

	// calculate C:d2WdCdC:C
	double CWWC = 2*I2*W2;

	// deviatoric cauchy-stress, trs = trace[s]/3
	mat3ds T = B*(W1 + W2*I1) - B2*W2;
	mat3ds devs = T.dev()*(2.0/J);

	// Identity tensor
	mat3ds I(1,1,1,0,0,0);

	tens4ds IxI = dyad1s(I);
	tens4ds I4  = dyad4s(I);
	tens4ds BxB = dyad1s(B);
	tens4ds B4  = dyad4s(B);

	// d2W/dCdC:C
	mat3ds WCCxC = B*(W2*I1) - B2*W2;

	tens4ds cw = (BxB - B4)*(W2*4.0*Ji) - dyad1s(WCCxC, I)*(4.0/3.0*Ji) + IxI*(4.0/9.0*Ji*CWWC);

	tens4ds c = dyad1s(devs, I)*(-2.0/3.0) + (I4 - IxI/3.0)*(4.0/3.0*Ji*WC) + cw;

	return c;
}

double CustomMaterial::DevStrainEnergyDensity(FEMaterialPoint& mp)
{
	FEElasticMaterialPoint& pt = *mp.ExtractData<FEElasticMaterialPoint>();
    
	// get material parameters
	double c1 = m_c1;
	double c2 = m_c2;

	// calculate deviatoric left Cauchy-Green tensor
	mat3ds B = pt.DevLeftCauchyGreen();
    
	// calculate square of B
	mat3ds B2 = B.sqr();
    
	// Invariants of B (= invariants of C)
	// Note that these are the invariants of Btilde, not of B!
	double I1 = B.tr();
	double I2 = 0.5*(I1*I1 - B2.tr());

	//
	// W = C1*(I1 - 3) + C2*(I2 - 3)
	//
    double sed = c1*(I1-3) + c2*(I2-3);
    
    // get data from custom material point
    auto &custom_point = *mp.ExtractData<CustomMaterialPoint>();

    return sed + custom_point.m_gamma; // add data from precice to result
}

FEMaterialPointData *CustomMaterial::CreateMaterialPointData()
{
    auto res = new CustomMaterialPoint(new FEElasticMaterialPoint);
    return res;
}
