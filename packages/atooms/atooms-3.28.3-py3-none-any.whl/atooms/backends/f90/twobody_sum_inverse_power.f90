module potential

  implicit none

  double precision, allocatable :: epsilon_(:,:,:)
  double precision, allocatable :: sigma_(:,:,:)
  integer, allocatable :: exponent_(:)
  integer :: order_

contains

  subroutine init(exponent, epsilon, sigma)
    integer, intent(in) :: exponent(:)
    double precision, intent(in) :: epsilon(:,:,:), sigma(:,:,:)
    if (allocated(epsilon_).and.allocated(sigma_)) return
    allocate(exponent_(size(exponent)), source=exponent)
    allocate(epsilon_(size(epsilon,1),size(epsilon,2),size(epsilon,3)), source=epsilon)
    allocate(sigma_(size(sigma,1),size(sigma,2),size(sigma,3)), source=sigma)
    order_ = size(exponent_)
  end subroutine init
  
  subroutine compute(isp,jsp,rsq,u,w,h)
    integer,          intent(in)    :: isp, jsp
    double precision, intent(in)    :: rsq
    double precision, intent(inout) :: u, w, h
    double precision                :: utmp
    integer                         :: i, order
    u = 0.d0
    w = 0.d0
    h = 0.d0
    do i = 1,order_
       ! Need to keep utmp local to each power with this recursive expression
       utmp = epsilon_(isp,jsp,i) * (sigma_(isp,jsp,i)**2 / rsq) ** (exponent_(i)/2)
       u = u + utmp
       w = w + exponent_(i) * utmp / rsq
       h = h + exponent_(i) * (exponent_(i)+2) * utmp / (rsq**2)
    end do
  end subroutine compute

end module potential
