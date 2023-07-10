#include <FEBioMech/FEActiveFiberContraction.h>
#include <FEBioMech/FETransIsoMooneyRivlin.h>
#include <FEBioMech/FEElasticMaterialPoint.h>

class FEBIOMECH_API CustomMaterialPoint : public FEElasticMaterialPoint
{
public:
    CustomMaterialPoint(FEMaterialPointData *mp = nullptr)
	    : FEElasticMaterialPoint(mp), m_gamma(0) {}

    double m_gamma;
};

class CustomContraction : public FEActiveFiberContraction
{
public:
    CustomContraction(FEModel *pfem)
	    : FEActiveFiberContraction(pfem) {}

    mat3ds ActiveStress(FEMaterialPoint &mp, const vec3d &a0) override;

    DECLARE_FECORE_CLASS();
};

class CustomMaterial : public FETransIsoMooneyRivlin
{
public:

    CustomMaterial(FEModel* pfem) 
	    : FETransIsoMooneyRivlin(pfem) {}

    FEMaterialPointData *CreateMaterialPointData() override;

    DECLARE_FECORE_CLASS();
};
