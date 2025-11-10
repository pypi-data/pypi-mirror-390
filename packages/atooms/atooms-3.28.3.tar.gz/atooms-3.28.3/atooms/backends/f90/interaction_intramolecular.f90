module interaction_intramolecular

  use helpers
  use bond_potential  !, only: compute
  
  implicit none

contains

  subroutine zeroing(for, epot, virial)
    double precision, intent(inout) :: for(:,:)
    double precision, intent(inout) :: epot, virial
    !$omp parallel workshare
    for = 0.0d0
    !$omp end parallel workshare
    epot = 0.0d0
    virial = 0.0d0    
  end subroutine zeroing
  
  subroutine forces_bond(zero,box,pos,spe,mol,rad,bond,bond_type,for,epot,virial)
    logical,          intent(in)    :: zero ! to set variables to zero
    double precision, intent(in)    :: box(:), pos(:,:), rad(:)
    integer,          intent(in)    :: spe(:), bond(:,:), bond_type(:)
    integer,          intent(in)    :: mol(:)  ! molecule to which particle belongs
    double precision, intent(inout) :: for(:,:)
    double precision, intent(inout) :: epot, virial
    double precision                :: rij(size(pos,1)), rijsq, uij, wij, hbox(size(pos,1)), hij
    integer                         :: ii, i, j, isp, jsp
    if (zero) then
       call zeroing(for, epot, virial)
    end if
    hbox = box / 2
    do ii = 1,size(bond,2)
       !print*, ii, size(bond,1), size(bond,2)
       i = bond(1,ii)
       j = bond(2,ii)
       isp = spe(mol(i))  ! species of the molecule to which particle i belongs
       jsp = bond_type(ii)
       call distance(i,j,pos,rij)
       call pbc(rij,box,hbox)
       call dot(rij,rij,rijsq)
       !call compute_stretch(isp,jsp,ksp,rijsq,uij,wij,hij) ! wij = -(du/dr)/r
       call compute_bond(isp,jsp,rijsq,uij,wij,hij) ! wij = -(du/dr)/r
       epot = epot + uij
       virial = virial + wij * rijsq
       for(:,i) = for(:,i) + wij * rij
       for(:,j) = for(:,j) - wij * rij
    end do
  end subroutine forces_bond

  ! subroutine forces_angle(zero,box,pos,spe,mol,rad,angle,angle_type,for,epot,virial)
  !   logical,          intent(in)    :: zero ! to set variables to zero
  !   double precision, intent(in)    :: box(:), pos(:,:), rad(:)
  !   integer,          intent(in)    :: spe(:), angle(:,:,:), angle_type(:)
  !   integer,          intent(in)    :: mol(:)  ! molecule to which particle belongs
  !   double precision, intent(inout) :: for(:,:)
  !   double precision, intent(inout) :: epot, virial
  !   double precision                :: rij(size(pos,1)), rijsq, uij, wij, hbox(size(pos,1)), hij
  !   integer                         :: ii, i, j, k, isp, jsp
  !   call zeroing(for, epot, virial)
  !   hbox = box / 2
  !   do ii = 1,size(angle,2)
  !      i = angle(1,ii)
  !      j = angle(2,ii)
  !      k = angle(3,ii)
  !      isp = spe(mol(i))  ! species of the molecule to which particle i belongs
  !      jsp = bond_type(ii)
  !      call distance(i,j,pos,rij)
  !      call pbc(rij,box,hbox)
  !      call dot(rij,rij,rijsq)
  !      !
  !      !call compute_angle(isp,jsp,ksp,rijsq,..........,uij,wij,hij) ! wij = -(du/dr)/r
  !      !
  !      epot = epot + uij
  !      virial = virial + wij * rijsq
  !      for(:,i) = for(:,i) + wij * rij
  !      for(:,j) = for(:,j) - wij * rij
  !   end do
  ! end subroutine forces_angle
  
end module interaction_intramolecular

