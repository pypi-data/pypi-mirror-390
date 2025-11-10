module angle_potential

  implicit none

  double precision, allocatable :: theta0_(:,:,:)
  double precision, allocatable :: K_(:,:,:)

contains

  subroutine init(theta0, K)
    double precision, intent(in) :: theta0(:,:,:), K(:,:,:)
    if (allocated(theta0_).and.allocated(K_)) return
    allocate(theta0_(size(theta0,1),size(theta0,2),size(theta0,3)), source=theta0)
    allocate(K_(size(K,1),size(K,2),size(K,3)), source=K)
  end subroutine init
  
  subroutine compute_angle(isp,jsp,ksp,rsq_ij,rsq_ik,rsq_jk,cos_theta_ijk,u,w,h)
    integer,          intent(in)    :: isp, jsp, ksp
    double precision, intent(in)    :: rsq_ij, rsq_ik, rsq_jk, cos_theta_ijk
    double precision, intent(inout) :: u, w, h
    double precision :: r, theta
    theta = acos(cos_theta_ijk)
    u = 0.5d0 * K_(isp,jsp,ksp) * (theta - theta0_(isp,jsp,ksp))**2
    w = K_(isp,jsp,ksp) * (theta - theta0_(isp,jsp,ksp))
    h = 0.0
  end subroutine compute_angle
  
end module angle_potential
