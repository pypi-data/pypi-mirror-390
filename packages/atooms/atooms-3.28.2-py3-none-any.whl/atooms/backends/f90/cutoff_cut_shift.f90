module cutoff

  use potential, init_potential => init
  
  implicit none

  double precision, allocatable :: rcut_(:,:)
  double precision, allocatable :: ucut(:,:)

contains

  subroutine init(rcut)
    double precision, intent(in) :: rcut(:,:)
    if (allocated(rcut_)) return
    allocate(rcut_(size(rcut,1),size(rcut,2)), source=rcut)
    call adjust()
  end subroutine init

  subroutine adjust()
    integer :: isp,jsp,nsp
    double precision :: rcutsq, u, w, h
    if (allocated(ucut)) return
    nsp = size(rcut_,1)
    allocate(ucut(nsp,nsp))
    do isp = 1,nsp
       do jsp = 1,nsp
          rcutsq = rcut_(isp,jsp)**2
          call compute(isp,jsp,rcutsq,ucut(isp,jsp),w,h)
       end do
    end do
  end subroutine adjust

  subroutine is_zero(isp,jsp,rsq,result)
    integer,          intent(in) :: isp, jsp
    double precision, intent(in) :: rsq
    logical,          intent(out) :: result
    result = rsq > rcut_(isp,jsp)**2
  end subroutine is_zero
  
  subroutine smooth(isp,jsp,rsq,uij,wij,hij)
    integer,          intent(in)    :: isp, jsp
    double precision, intent(in)    :: rsq
    double precision, intent(inout) :: uij,wij,hij
    uij = uij - ucut(isp,jsp)
    wij = wij
    hij = hij
  end subroutine smooth

  ! subroutine smooth_vector(isp,jsp,rsq,uij,wij,hij)
  !   integer,          intent(in)    :: isp, jsp(:)
  !   double precision, intent(in)    :: rsq(:)
  !   double precision, intent(inout) :: uij(:),wij(:),hij(:)
  !   integer                         :: i
  !   do i = 1,size(uij)
  !      uij(i) = uij(i) - ucut(isp,jsp(i))
  !   end do
  !   !uij = [(uij(i) - ucut(isp,jsp(i)), i=1,size(uij))]
  !   wij = wij
  !   hij = hij
  ! end subroutine smooth_vector
  
end module cutoff
