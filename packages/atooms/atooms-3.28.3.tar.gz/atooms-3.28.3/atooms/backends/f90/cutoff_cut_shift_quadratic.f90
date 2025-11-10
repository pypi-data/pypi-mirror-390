module cutoff

  use potential, init_potential => init
  
  implicit none

  double precision, allocatable :: rcut_(:,:)
  double precision, allocatable :: a_cut(:,:)
  double precision, allocatable :: b_cut(:,:)

contains

  subroutine init(rcut)
    double precision, intent(in) :: rcut(:,:)
    if (allocated(rcut_)) return
    allocate(rcut_(size(rcut,1),size(rcut,2)), source=rcut)
    call adjust()
  end subroutine init

  subroutine adjust()
    ! note that U'=-u1*radius 
    !   A = - 0.5*U'(r_c)/r_c
    !   B =   0.5*U'(r_c)*r_c - U(r_c) 
    ! so that
    !   U_qs(r) = U(r) + A*r^2 + B
    ! is smooth up to its first derivative at r=r_c
    integer :: isp,jsp,nsp
    double precision :: rcutsq, u, w, h
    if (allocated(a_cut)) return
    allocate(a_cut(size(rcut_,1),size(rcut_,2)))
    allocate(b_cut(size(rcut_,1),size(rcut_,2)))
    nsp = size(rcut_,1)
    do isp = 1,nsp
       do jsp = 1,nsp
          rcutsq = rcut_(isp,jsp)**2
          call compute(isp,jsp,rcutsq,u,w,h)
          a_cut(isp,jsp) =   0.5d0 * w
          b_cut(isp,jsp) = - 0.5d0 * w * rcutsq - u
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
    uij = uij + a_cut(isp,jsp) * rsq + b_cut(isp,jsp)
    wij = wij - a_cut(isp,jsp) * 2.d0
    hij = hij
  end subroutine smooth
  
end module cutoff
