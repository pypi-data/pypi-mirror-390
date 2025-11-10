module potential

  implicit none

  double precision, allocatable :: epsilon_(:,:)
  double precision, allocatable :: sigma_(:,:)

contains

  subroutine init(epsilon, sigma)
    double precision, intent(in) :: epsilon(:,:), sigma(:,:)
    if (allocated(epsilon_).and.allocated(sigma_)) return
    allocate(epsilon_(size(epsilon,1),size(epsilon,2)), source=epsilon)
    allocate(sigma_(size(sigma,1),size(sigma,2)), source=sigma)
  end subroutine init
  
  subroutine compute(isp,jsp,rsq,u,w,h)
    integer,          intent(in)    :: isp, jsp
    double precision, intent(in)    :: rsq
    double precision, intent(inout) :: u, w, h
    u = epsilon_(isp,jsp) * exp(- rsq / sigma_(isp,jsp)**2)
    w = 2 * u
    h = 4 * u
  end subroutine compute

end module potential
