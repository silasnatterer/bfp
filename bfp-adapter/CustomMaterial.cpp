#include "CustomMaterial.h"

BEGIN_FECORE_CLASS(CustomMaterial, FETransIsoMooneyRivlin)
	ADD_PARAMETER(m_c1, "c1");
	ADD_PARAMETER(m_c2, "c2");
	ADD_PARAMETER(m_fib.m_c3, "c3");
	ADD_PARAMETER(m_fib.m_c4, "c4");
	ADD_PARAMETER(m_fib.m_c5, "c5");
	ADD_PARAMETER(m_fib.m_lam1, "lam_max");
	ADD_PROPERTY(m_fiber, "fiber")->SetDefaultType("vector");
	ADD_PROPERTY(m_ac, "active_contraction", FEProperty::Optional);
END_FECORE_CLASS();

BEGIN_FECORE_CLASS(CustomContraction, FEActiveFiberContraction)
	ADD_PARAMETER(m_ascl , "ascl");
	ADD_PARAMETER(m_Tmax , "Tmax");
	ADD_PARAMETER(m_ca0  , "ca0");
	ADD_PARAMETER(m_camax, "camax");
	ADD_PARAMETER(m_beta , "beta");
	ADD_PARAMETER(m_l0   , "l0");
	ADD_PARAMETER(m_refl , "refl");
END_FECORE_CLASS();


FEMaterialPointData *CustomMaterial::CreateMaterialPointData()
{
    auto res = new CustomMaterialPoint;
    if (m_ac) res->Append(m_ac->CreateMaterialPointData());
    return res;
}

mat3ds CustomContraction::ActiveStress(FEMaterialPoint& mp, const vec3d& a0)
{
	CustomMaterialPoint& pt = *mp.ExtractData<CustomMaterialPoint>();

	// get the deformation gradient
	mat3d F = pt.m_F;
	double J = pt.m_J;
	double Jm13 = pow(J, -1.0 / 3.0);

	// calculate the current material axis lam*a = F*a0;
	vec3d a = F*a0;

	// normalize material axis and store fiber stretch
	double lam, lamd;
	lam = a.unit();
	lamd = lam*Jm13; // i.e. lambda tilde

	// calculate dyad of a: AxA = (a x a)
	mat3ds AxA = dyad(a);

	// get the activation
	double saf = pt.m_gamma;
	return AxA*saf;
}

