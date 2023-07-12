#include "DiHuMaterial.h"

BEGIN_FECORE_CLASS(DiHuMaterial, FETransIsoMooneyRivlin)
	ADD_PARAMETER(m_c1, "c1");
	ADD_PARAMETER(m_c2, "c2");
	ADD_PARAMETER(m_fib.m_c3, "c3");
	ADD_PARAMETER(m_fib.m_c4, "c4");
	ADD_PARAMETER(m_fib.m_c5, "c5");
	ADD_PARAMETER(m_fib.m_lam1, "lam_max");
	ADD_PROPERTY(m_fiber, "fiber")->SetDefaultType("vector");
	ADD_PROPERTY(m_ac, "active_contraction", FEProperty::Optional);
END_FECORE_CLASS();

// Create DiHuMaterialPoint instead of FEElasticMaterialPoint
FEMaterialPointData *DiHuMaterial::CreateMaterialPointData() {
    	auto pt = new DiHuMaterialPoint;
    	if (m_ac) pt->Append(m_ac->CreateMaterialPointData());
    	return pt;
}

BEGIN_FECORE_CLASS(DiHuContraction, FEActiveContractionMaterial)
	ADD_PARAMETER(m_pmax, "pmax");
END_FECORE_CLASS();

// Uses OpenDiHus active stress calculation
mat3ds DiHuContraction::ActiveStress(FEMaterialPoint &mp, const vec3d &a0) {
	DiHuMaterialPoint &pt = *mp.ExtractData<DiHuMaterialPoint>();

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

	// Calculate active stress using OpenDiHus formula
	double lam_opt = 1.2; // constant in OpenDiHu 
	double arg = lam/lam_opt;
	double f = -(25/4)*arg*arg + (25/2)*arg - 5.25;
	double saf = (1/lam) * m_pmax * f * pt.m_gamma;

	return AxA*saf;
}

// Do not use active stiffness
tens4ds DiHuContraction::ActiveStiffness(FEMaterialPoint &mp, const vec3d &a0) {
	return tens4ds(0.0);
}
