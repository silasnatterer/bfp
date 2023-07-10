#include <FEBioMech/FEUncoupledMaterial.h>
#include <FEBioMech/FEElasticMaterialPoint.h>

class FEBIOMECH_API CustomMaterialPoint : public FEMaterialPointData
{
public:
    CustomMaterialPoint(FEMaterialPointData *mp): FEMaterialPointData(mp)
    {
        m_gamma = 0.;
    }

    double m_gamma;
};

class CustomMaterial : public FEUncoupledMaterial
{
public:

    CustomMaterial(FEModel* pfem);

    // material parameters
    double  m_c1;
    double  m_c2;

    // Cauchy-stress calculation
    mat3ds DevStress(FEMaterialPoint& pt) override;
    // Spatial elasticity tensor calculation
    tens4ds DevTangent(FEMaterialPoint& pt) override;
    // Deviatoric strain energy density calculation
	double DevStrainEnergyDensity(FEMaterialPoint& mp) override;

    // class initialization (optional)
    bool Init() override;
    // class validation (optional)
    bool Validate() override;

    FEMaterialPointData *CreateMaterialPointData() override;

    // required macro for integrating this class with FECore
    DECLARE_FECORE_CLASS();
};
