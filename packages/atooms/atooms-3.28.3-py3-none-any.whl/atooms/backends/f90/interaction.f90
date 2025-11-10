 
module interaction

  use helpers
  use cutoff  !, only: is_zero, smooth, adjust
  use potential  !, only: compute
  
  implicit none

contains

  subroutine energies(zero,box,pos,ids,rad,epot)
    logical,          intent(in)    :: zero ! to set variables to zero
    double precision, intent(in)    :: box(:)
    double precision, intent(in)    :: pos(:,:)
    integer,          intent(in)    :: ids(:)
    double precision, intent(in)    :: rad(:)  ! not used here
    double precision, intent(inout) :: epot(:)
    double precision                :: rij(size(pos,1)), rijsq, uij, wij, hbox(size(pos,1)), hij
    integer                         :: i, j, isp, jsp
    logical                         :: zero_ij
    if (zero) then
       !$omp parallel workshare
       epot = 0.0d0
       !$omp end parallel workshare
    end if
    hbox = box / 2
    ! it is crucial to use default(firstprivate) otherwise the shared module-level variables of cutoffs and potentials are not copied!
    !$omp parallel default(firstprivate) shared(pos,ids,box,hbox,epot)
    !$omp do schedule(runtime) reduction(+:epot)
    do i = 1,size(pos,2)
       isp = ids(i)
       do j = i+1,size(pos,2)
          jsp = ids(j)
          call distance(i,j,pos,rij)
          call pbc(rij,box,hbox)
          call dot(rij,rij,rijsq)
          call is_zero(isp,jsp,rijsq,zero_ij)
          if (.not.zero_ij) then
             call compute(isp,jsp,rijsq,uij,wij,hij) ! wij = -(du/dr)/r
             call smooth(isp,jsp,rijsq,uij,wij,hij) ! wij = -(du/dr)/r
             epot(i) = epot(i) + uij
             epot(j) = epot(j) + uij
          end if
       end do
    end do
    !$omp end parallel
  end subroutine energies

  subroutine forces(zero,box,pos,ids,rad,for,epot,virial)
    logical,          intent(in)    :: zero ! to set variables to zero
    double precision, intent(in)    :: box(:)
    double precision, intent(in)    :: pos(:,:)
    integer,          intent(in)    :: ids(:)
    double precision, intent(in)    :: rad(:)  ! not used here
    double precision, intent(inout) :: for(:,:)
    double precision, intent(inout) :: epot, virial  ! inout to allow in place modification
    double precision                :: rij(size(pos,1)), rijsq, uij, wij, hbox(size(pos,1)), hij
    integer                         :: i, j, isp, jsp
    logical                         :: zero_ij
    ! TODO: it should be possible to adjust the cutoff from python, but the compute interface is not parsed correctly
    if (zero) then
       !$omp parallel workshare
       for = 0.0d0
       !$omp end parallel workshare
       epot = 0.0d0
       virial = 0.0d0
    end if
    hbox = box / 2
    !omp parallel do private(isp,jsp,rij,rijsq,zero_ij,uij,wij) schedule(runtime) reduction(+:epot,virial,for)
    ! it is crucial to use default(firstprivate) otherwise the shared module-level variables of cutoffs and potentials are not copied!
    !$omp parallel default(firstprivate) shared(pos,ids,box,hbox,epot,virial,for)
    !$omp do schedule(runtime) reduction(+:epot,virial,for)
    do i = 1,size(pos,2)
       isp = ids(i)
       do j = i+1,size(pos,2)
          jsp = ids(j)
          call distance(i,j,pos,rij)
          call pbc(rij,box,hbox)
          call dot(rij,rij,rijsq)
          call is_zero(isp,jsp,rijsq,zero_ij)
          if (.not.zero_ij) then
             ! TODO: remove hij via interface             
             call compute(isp,jsp,rijsq,uij,wij,hij) ! wij = -(du/dr)/r
             call smooth(isp,jsp,rijsq,uij,wij,hij) ! wij = -(du/dr)/r
             !print*, isp, jsp, rijsq**0.5, uij, wij
             epot = epot + uij
             virial = virial + wij * rijsq
             for(:,i) = for(:,i) + wij * rij
             for(:,j) = for(:,j) - wij * rij
          end if
       end do
    end do
    !$omp end parallel
  end subroutine forces
  
  subroutine hessian(zero,box,pos,ids,rad,hes)
    logical,          intent(in)    :: zero ! to set variables to zero
    double precision, intent(in)    :: box(:)
    double precision, intent(in)    :: pos(:,:)
    integer,          intent(in)    :: ids(:)
    double precision, intent(in)    :: rad(:)  ! not used here
    !double precision, intent(inout) :: hes(size(pos,1),size(pos,2),size(pos,1),size(pos,2))
    double precision, intent(inout) :: hes(:,:,:,:)
    double precision                :: rij(size(pos,1)), rijsq, uij, wij, wwij, hbox(size(pos,1))
    double precision                :: unity(size(pos,1),size(pos,1)), mij(size(pos,1),size(pos,1)), mmij(size(pos,1),size(pos,1))
    integer                         :: i, j, isp, jsp
    logical                         :: zero_ij
    if (zero) hes = 0.0d0
    unity = 0.0d0
    hbox = box / 2
    do i = 1,size(unity,1)
       unity(i,i) = 1.0d0
    end do
    loop_i: do i = 1,size(pos,2)
       isp = ids(i)
       loop_j: do j = i+1,size(pos,2)          
          jsp = ids(j)
          rij = pos(:,i) - pos(:,j)
          call pbc(rij,box,hbox)
          rijsq = dot_product(rij,rij)
          call is_zero(isp,jsp,rijsq,zero_ij)
          if (.not.zero_ij) then
             call compute(isp,jsp,rijsq,uij,wij,wwij)
             call smooth(isp,jsp,rijsq,uij,wij,wwij)
             mij = unity(:,:) * wij
             mmij = outer_product(rij,rij) * wwij
             ! Diagonal in i,j - diagonal in x,y
             hes(:,i,:,i) = hes(:,i,:,i) - mij
             hes(:,j,:,j) = hes(:,j,:,j) - mij
             ! Off-diagonal in i,j - diagonal in x,y
             hes(:,i,:,j) = hes(:,i,:,j) + mij
             hes(:,j,:,i) = hes(:,j,:,i) + mij
             ! Diagonal in i,j - off-diagonal in x,y
             hes(:,i,:,i) = hes(:,i,:,i) + mmij
             hes(:,j,:,j) = hes(:,j,:,j) + mmij
             ! Off-diagonal in i,j - off-diagonal in x,y
             hes(:,i,:,j) = hes(:,i,:,j) - mmij
             hes(:,j,:,i) = hes(:,j,:,i) - mmij
          end if
       end do loop_j
    end do loop_i
  end subroutine hessian

  subroutine gradw(zero,box,pos,ids,rad,grad_w)
    logical,          intent(in)    :: zero ! to set variables to zero
    double precision, intent(in)    :: box(:)
    double precision, intent(in)    :: pos(:,:)
    integer,  intent(in)            :: ids(:)
    double precision, intent(in)    :: rad(:)  ! not used here
    double precision, intent(inout) :: grad_w(:,:)
    double precision                :: rij(size(pos,1)), rijsq, uij, wij, wwij
    double precision                :: hbox(size(pos,1)), grwij(size(pos,1)), forc(size(pos,1),size(pos,2)), epot, virial
    integer                         :: i, j, isp, jsp
    logical                         :: zero_ij
    call forces(.TRUE.,box,pos,ids,rad,forc,epot,virial)
    if (zero) grad_w = 0.d0
    hbox = box / 2
    loop_i: do i = 1,size(pos,2)
       isp = ids(i)
       loop_j: do j = i+1,size(pos,2)          
          jsp = ids(j)
          call distance(i,j,pos,rij)
          call pbc(rij,box,hbox)
          call dot(rij,rij,rijsq)
          call is_zero(isp,jsp,rijsq,zero_ij)          
          if (.not.zero_ij) then
             call compute(isp,jsp,rijsq,uij,wij,wwij)
             call smooth(isp,jsp,rijsq,uij,wij,wwij)
             ! Signs are reversed compared to f90atooms...
             grwij = wij * forc(:,i) - rij(:) * (wwij * DOT_PRODUCT(rij(:),forc(:,i)))
             grad_w(:,i) = grad_w(:,i) + grwij(:)
             grad_w(:,j) = grad_w(:,j) - grwij(:)
             grwij = wij * forc(:,j) - rij(:) * (wwij * DOT_PRODUCT(rij(:),forc(:,j)))
             grad_w(:,i) = grad_w(:,i) - grwij(:)
             grad_w(:,j) = grad_w(:,j) + grwij(:)
          end if
       end do loop_j
    end do loop_i
    grad_w = grad_w * 2
  end subroutine gradw
  
end module interaction

module interaction_neighbors

  use helpers
  use cutoff  !, only: is_zero, smooth, adjust
  use potential  !, only: compute
  
  implicit none

contains

  subroutine energies(zero,box,pos,ids,rad,neighbors,number_neighbors,epot)
    logical,          intent(in)    :: zero ! to set variables to zero
    double precision, intent(in)    :: box(:)
    double precision, intent(in)    :: pos(:,:)
    integer,          intent(in)    :: ids(:)
    double precision, intent(in)    :: rad(:)  ! not used here
    integer,          intent(in)    :: neighbors(:,:), number_neighbors(:)
    double precision, intent(inout) :: epot(:)
    double precision                :: rij(size(pos,1)), rijsq, uij, hbox(size(pos,1)), hij, wij
    integer                         :: i, j, isp, jsp, jn
    logical                         :: zero_ij
    if (zero) then
       !$omp parallel workshare
       epot = 0.0d0
       !$omp end parallel workshare
    end if
    hbox = box / 2
    ! it is crucial to use default(firstprivate) otherwise the shared module-level variables of cutoffs and potentials are not copied!
    !$omp parallel default(firstprivate) shared(pos,ids,box,hbox,epot)
    !$omp do schedule(runtime) reduction(+:epot)
    do i = 1,size(pos,2)
       isp = ids(i)
       do jn = 1,number_neighbors(i)
          j = neighbors(jn,i)
          !if (newton) then
          !   if (j<i) cycle
          !end if
          jsp = ids(j)
          call distance(i,j,pos,rij)
          call pbc(rij,box,hbox)
          call dot(rij,rij,rijsq)
          call is_zero(isp,jsp,rijsq,zero_ij)          
          if (.not.zero_ij) then
             ! TODO: remove hij via interface             
             call compute(isp,jsp,rijsq,uij,wij,hij) ! wij = -(du/dr)/r
             call smooth(isp,jsp,rijsq,uij,wij,hij) ! wij = -(du/dr)/r
             epot(i) = epot(i) + uij
             epot(j) = epot(j) + uij
          end if
       end do
    end do
    !$omp end parallel
  end subroutine energies

  subroutine forces(zero,box,pos,ids,rad,neighbors,number_neighbors,for,epot,virial)
    logical,          intent(in)    :: zero ! to set variables to zero
    double precision, intent(in)    :: box(:)
    double precision, intent(in)    :: pos(:,:)
    integer,          intent(in)    :: ids(:)
    double precision, intent(in)    :: rad(:)  ! not used here
    integer,          intent(in)    :: neighbors(:,:), number_neighbors(:)
    double precision, intent(inout) :: for(:,:)
    double precision, intent(inout) :: epot, virial
    double precision                :: rij(size(pos,1)), rijsq, uij, wij, hbox(size(pos,1)), hij
    integer                         :: i, j, isp, jsp, jn
    logical                         :: zero_ij
    ! TODO: it should be possible to adjust the cutoff from python, but the compute interface is not parsed correctly
    if (zero) then
       !$omp parallel workshare
       for = 0.0d0
       !$omp end parallel workshare
       epot = 0.0d0
       virial = 0.0d0
    end if
    hbox = box / 2
    ! it is crucial to use default(firstprivate) otherwise the shared module-level variables of cutoffs and potentials are not copied!
    !$omp parallel default(firstprivate) shared(pos,ids,box,hbox,epot,virial,for)
    !$omp do schedule(runtime) reduction(+:epot,virial,for)
    do i = 1,size(pos,2)
       isp = ids(i)
       do jn = 1,number_neighbors(i)
          j = neighbors(jn,i)
          !if (newton) then
          !   if (j<i) cycle
          !end if
          jsp = ids(j)
          call distance(i,j,pos,rij)
          call pbc(rij,box,hbox)
          call dot(rij,rij,rijsq)
          call is_zero(isp,jsp,rijsq,zero_ij)          
          if (.not.zero_ij) then
             ! TODO: remove hij via interface             
             call compute(isp,jsp,rijsq,uij,wij,hij) ! wij = -(du/dr)/r
             call smooth(isp,jsp,rijsq,uij,wij,hij) ! wij = -(du/dr)/r
             !print*, isp, jsp, rijsq**0.5, uij, wij
             epot = epot + uij
             virial = virial + wij * rijsq
             for(:,i) = for(:,i) + wij * rij
             for(:,j) = for(:,j) - wij * rij
          end if
       end do
    end do
    !$omp end parallel
  end subroutine forces
  
  subroutine hessian(zero,box,pos,ids,rad,neighbors,number_neighbors,hes)
    logical,          intent(in)    :: zero ! to set variables to zero
    double precision, intent(in)    :: box(:)
    double precision, intent(in)    :: pos(:,:)
    integer,          intent(in)    :: ids(:)
    double precision, intent(in)    :: rad(:)  ! not used here
    integer,          intent(in)    :: neighbors(:,:), number_neighbors(:)
    !double precision, intent(inout) :: hes(size(pos,1),size(pos,2),size(pos,1),size(pos,2))
    double precision, intent(inout) :: hes(:,:,:,:)
    double precision                :: rij(size(pos,1)), rijsq, uij, wij, wwij, hbox(size(pos,1))
    double precision                :: unity(size(pos,1),size(pos,1)), mij(size(pos,1),size(pos,1)), mmij(size(pos,1),size(pos,1))
    integer                         :: i, j, isp, jsp, jn
    logical                         :: zero_ij
    if (zero) hes = 0.0d0
    unity = 0.0d0
    hbox = box / 2
    do i = 1,size(unity,1)
       unity(i,i) = 1.0d0
    end do
    loop_i: do i = 1,size(pos,2)
       isp = ids(i)
       loop_j: do jn = 1,number_neighbors(i)
          j = neighbors(jn,i)
          jsp = ids(j)
          rij = pos(:,i) - pos(:,j)
          call pbc(rij,box,hbox)
          rijsq = dot_product(rij,rij)
          call is_zero(isp,jsp,rijsq,zero_ij)
          if (.not.zero_ij) then
             call compute(isp,jsp,rijsq,uij,wij,wwij)
             call smooth(isp,jsp,rijsq,uij,wij,wwij)
             mij = unity(:,:) * wij
             mmij = outer_product(rij,rij) * wwij
             ! Diagonal in i,j - diagonal in x,y
             hes(:,i,:,i) = hes(:,i,:,i) - mij
             hes(:,j,:,j) = hes(:,j,:,j) - mij
             ! Off-diagonal in i,j - diagonal in x,y
             hes(:,i,:,j) = hes(:,i,:,j) + mij
             hes(:,j,:,i) = hes(:,j,:,i) + mij
             ! Diagonal in i,j - off-diagonal in x,y
             hes(:,i,:,i) = hes(:,i,:,i) + mmij
             hes(:,j,:,j) = hes(:,j,:,j) + mmij
             ! Off-diagonal in i,j - off-diagonal in x,y
             hes(:,i,:,j) = hes(:,i,:,j) - mmij
             hes(:,j,:,i) = hes(:,j,:,i) - mmij
          end if
       end do loop_j
    end do loop_i
  end subroutine hessian

end module interaction_neighbors

module interaction_polydisperse

  use helpers
  use cutoff  !, only: is_zero, smooth, adjust
  use potential  !, only: compute
  
  implicit none

contains

  subroutine forces(zero,box,pos,ids,rad,for,epot,virial)
    logical,          intent(in)    :: zero ! to set variables to zero
    double precision, intent(in)    :: box(:)
    double precision, intent(in)    :: pos(:,:)
    integer,          intent(in)    :: ids(:)
    double precision, intent(in)    :: rad(:)
    double precision, intent(inout) :: for(:,:)
    double precision, intent(inout) :: epot, virial
    double precision                :: rij(size(pos,1)), rijsq, uij, wij, hbox(size(pos,1)), hij
    integer                         :: i, j, isp, jsp
    logical                         :: zero_ij
    ! TODO: it should be possible to adjust the cutoff from python, but the compute interface is not parsed correctly
    if (zero) then
       !$omp parallel workshare
       for = 0.0d0
       !$omp end parallel workshare
       epot = 0.0d0
       virial = 0.0d0
    end if
    hbox = box / 2
    !omp parallel do private(isp,jsp,rij,rijsq,zero_ij,uij,wij) schedule(runtime) reduction(+:epot,virial,for)
    ! it is crucial to use default(firstprivate) otherwise the shared module-level variables of cutoffs and potentials are not copied!
    !$omp parallel default(firstprivate) shared(pos,ids,box,hbox,epot,virial,for)
    !$omp do schedule(runtime) reduction(+:epot,virial,for)
    do i = 1,size(pos,2)
       isp = ids(i)
       do j = i+1,size(pos,2)
          jsp = ids(j)
          call distance(i,j,pos,rij)
          call pbc(rij,box,hbox)
          call dot(rij,rij,rijsq)
          rijsq = rijsq / (rad(i)+rad(j))**2
          call is_zero(isp,jsp,rijsq,zero_ij)
          if (.not.zero_ij) then
             ! TODO: remove hij via interface             
             call compute(isp,jsp,rijsq,uij,wij,hij) ! wij = -(du/dr)/r
             call smooth(isp,jsp,rijsq,uij,wij,hij) ! wij = -(du/dr)/r
             epot = epot + uij
             ! w = - 1/rad_ij   * du/dr_ij(r_ij/rad_ij) * r_ij
             !   = - 1/rad_ij^2 * du/dr_ij(x) * x^2  with x=r_ij/rad_ij
             ! The scaled rijsq already contains 1/rad_ij^2
             virial = virial + wij * rijsq
             ! We must scale wij for the forces here
             wij = wij / (rad(i)+rad(j))**2
             for(:,i) = for(:,i) + wij * rij
             for(:,j) = for(:,j) - wij * rij
          end if
       end do
    end do
    !$omp end parallel
  end subroutine forces

  subroutine hessian(zero,box,pos,ids,rad,hes)
    logical,          intent(in)    :: zero ! to set variables to zero
    double precision, intent(in)    :: box(:)
    double precision, intent(in)    :: pos(:,:)
    integer,          intent(in)    :: ids(:)
    double precision, intent(in)    :: rad(:)
    !double precision, intent(inout) :: hes(size(pos,1),size(pos,2),size(pos,1),size(pos,2))
    double precision, intent(inout) :: hes(:,:,:,:)
    double precision                :: rij(size(pos,1)), rijsq, uij, wij, wwij, hbox(size(pos,1))
    double precision                :: unity(size(pos,1),size(pos,1)), mij(size(pos,1),size(pos,1)), mmij(size(pos,1),size(pos,1))
    integer                         :: i, j, isp, jsp
    logical                         :: zero_ij
    if (zero) hes = 0.0d0
    unity = 0.0d0
    hbox = box / 2
    do i = 1,size(unity,1)
       unity(i,i) = 1.0d0
    end do
    loop_i: do i = 1,size(pos,2)
       isp = ids(i)
       loop_j: do j = i+1,size(pos,2)          
          jsp = ids(j)
          rij = pos(:,i) - pos(:,j)
          call pbc(rij,box,hbox)
          call dot(rij,rij,rijsq)
          rijsq = rijsq / (rad(i)+rad(j))**2
          call is_zero(isp,jsp,rijsq,zero_ij)
          if (.not.zero_ij) then
             call compute(isp,jsp,rijsq,uij,wij,wwij)
             call smooth(isp,jsp,rijsq,uij,wij,wwij)
             wij = wij / (rad(i)+rad(j))**2
             wwij = wwij / (rad(i)+rad(j))**4
             mij = unity(:,:) * wij
             mmij = outer_product(rij,rij) * wwij
             ! Diagonal in i,j - diagonal in x,y
             hes(:,i,:,i) = hes(:,i,:,i) - mij
             hes(:,j,:,j) = hes(:,j,:,j) - mij
             ! Off-diagonal in i,j - diagonal in x,y
             hes(:,i,:,j) = hes(:,i,:,j) + mij
             hes(:,j,:,i) = hes(:,j,:,i) + mij
             ! Diagonal in i,j - off-diagonal in x,y
             hes(:,i,:,i) = hes(:,i,:,i) + mmij
             hes(:,j,:,j) = hes(:,j,:,j) + mmij
             ! Off-diagonal in i,j - off-diagonal in x,y
             hes(:,i,:,j) = hes(:,i,:,j) - mmij
             hes(:,j,:,i) = hes(:,j,:,i) - mmij
          end if
       end do loop_j
    end do loop_i
  end subroutine hessian

  subroutine gradw(zero,box,pos,ids,rad,grad_w)
    logical,          intent(in)    :: zero ! to set variables to zero
    double precision, intent(in)    :: box(:)
    double precision, intent(in)    :: pos(:,:)
    integer,          intent(in)    :: ids(:)
    double precision, intent(in)    :: rad(:)
    double precision, intent(inout) :: grad_w(:,:)
    double precision                :: rij(size(pos,1)), rijsq, uij, wij, wwij
    double precision                :: hbox(size(pos,1)), grwij(size(pos,1)), forc(size(pos,1),size(pos,2)), epot, virial
    integer                         :: i, j, isp, jsp
    logical                         :: zero_ij
    call forces(.FALSE.,box,pos,ids,rad,forc,epot,virial)
    if (zero) grad_w = 0.d0
    hbox = box / 2
    loop_i: do i = 1,size(pos,2)
       isp = ids(i)
       loop_j: do j = i+1,size(pos,2)          
          jsp = ids(j)
          call distance(i,j,pos,rij)
          call pbc(rij,box,hbox)
          call dot(rij,rij,rijsq)
          rijsq = rijsq / (rad(i)+rad(j))**2
          call is_zero(isp,jsp,rijsq,zero_ij)          
          if (.not.zero_ij) then
             call compute(isp,jsp,rijsq,uij,wij,wwij)
             call smooth(isp,jsp,rijsq,uij,wij,wwij)
             wij = wij / (rad(i)+rad(j))**2
             wwij = wwij / (rad(i)+rad(j))**4
             ! Signs are reversed compared to f90atooms...
             grwij = wij * forc(:,i) - rij(:) * (wwij * DOT_PRODUCT(rij(:),forc(:,i)))
             grad_w(:,i) = grad_w(:,i) + grwij(:)
             grad_w(:,j) = grad_w(:,j) - grwij(:)
             grwij = wij * forc(:,j) - rij(:) * (wwij * DOT_PRODUCT(rij(:),forc(:,j)))
             grad_w(:,i) = grad_w(:,i) - grwij(:)
             grad_w(:,j) = grad_w(:,j) + grwij(:)
          end if
       end do loop_j
    end do loop_i
    grad_w = grad_w * 2
  end subroutine gradw
  
end module interaction_polydisperse

module interaction_polydisperse_neighbors

  use helpers
  use cutoff  !, only: is_zero, smooth, adjust
  use potential  !, only: compute
  
  implicit none

contains

  subroutine energies(zero,box,pos,ids,rad,neighbors,number_neighbors,epot)
    logical,          intent(in)    :: zero ! to set variables to zero
    double precision, intent(in)    :: box(:)
    double precision, intent(in)    :: pos(:,:)
    integer,          intent(in)    :: ids(:)
    double precision, intent(in)    :: rad(:)  ! not used here
    integer,          intent(in)    :: neighbors(:,:), number_neighbors(:)
    double precision, intent(inout) :: epot(:)
    double precision                :: rij(size(pos,1)), rijsq, uij, hbox(size(pos,1)), hij, wij
    integer                         :: i, j, isp, jsp, jn
    logical                         :: zero_ij
    if (zero) then
       !$omp parallel workshare
       epot = 0.0d0
       !$omp end parallel workshare
    end if
    hbox = box / 2
    ! it is crucial to use default(firstprivate) otherwise the shared module-level variables of cutoffs and potentials are not copied!
    !$omp parallel default(firstprivate) shared(pos,ids,box,hbox,epot)
    !$omp do schedule(runtime) reduction(+:epot)
    do i = 1,size(pos,2)
       isp = ids(i)
       do jn = 1,number_neighbors(i)
          j = neighbors(jn,i)
          !if (newton) then
          !   if (j<i) cycle
          !end if
          jsp = ids(j)
          call distance(i,j,pos,rij)
          call pbc(rij,box,hbox)
          call dot(rij,rij,rijsq)
          rijsq = rijsq / (rad(i)+rad(j))**2
          call is_zero(isp,jsp,rijsq,zero_ij)          
          if (.not.zero_ij) then
             ! TODO: remove hij via interface             
             call compute(isp,jsp,rijsq,uij,wij,hij) ! wij = -(du/dr)/r
             call smooth(isp,jsp,rijsq,uij,wij,hij) ! wij = -(du/dr)/r
             epot(i) = epot(i) + uij
             epot(j) = epot(j) + uij
          end if
       end do
    end do
    !$omp end parallel
  end subroutine energies

  subroutine forces(zero,box,pos,ids,rad,neighbors,number_neighbors,for,epot,virial)
    logical,          intent(in)    :: zero ! to set variables to zero
    double precision, intent(in)    :: box(:)
    double precision, intent(in)    :: pos(:,:)
    integer,          intent(in)    :: ids(:)
    double precision, intent(in)    :: rad(:)  ! not used here
    integer,          intent(in)    :: neighbors(:,:), number_neighbors(:)
    double precision, intent(inout) :: for(:,:)
    double precision, intent(inout) :: epot, virial
    double precision                :: rij(size(pos,1)), rijsq, uij, wij, hbox(size(pos,1)), hij
    integer                         :: i, j, isp, jsp, jn
    logical                         :: zero_ij
    ! TODO: it should be possible to adjust the cutoff from python, but the compute interface is not parsed correctly
    if (zero) then
       !$omp parallel workshare
       for = 0.0d0
       !$omp end parallel workshare
       epot = 0.0d0
       virial = 0.0d0
    end if
    hbox = box / 2
    ! it is crucial to use default(firstprivate) otherwise the shared module-level variables of cutoffs and potentials are not copied!
    !$omp parallel default(firstprivate) shared(pos,ids,rad,box,hbox,epot,virial,for)
    !$omp do schedule(runtime) reduction(+:epot,virial,for)
    do i = 1,size(pos,2)
       isp = ids(i)
       do jn = 1,number_neighbors(i)
          j = neighbors(jn,i)
          !if (newton) then
          !   if (j<i) cycle
          !end if
          jsp = ids(j)
          call distance(i,j,pos,rij)
          call pbc(rij,box,hbox)
          call dot(rij,rij,rijsq)
          rijsq = rijsq / (rad(i)+rad(j))**2
          call is_zero(isp,jsp,rijsq,zero_ij)          
          if (.not.zero_ij) then
             ! TODO: remove hij via interface             
             call compute(isp,jsp,rijsq,uij,wij,hij) ! wij = -(du/dr)/r
             call smooth(isp,jsp,rijsq,uij,wij,hij) ! wij = -(du/dr)/r
             !print*, isp, jsp, rijsq**0.5, uij, wij
             epot = epot + uij
             ! The scaled rijsq already contains 1/rad_ij^2
             virial = virial + wij * rijsq
             ! We must scale wij for the forces here
             wij = wij / (rad(i)+rad(j))**2
             for(:,i) = for(:,i) + wij * rij
             for(:,j) = for(:,j) - wij * rij
          end if
       end do
    end do
    !$omp end parallel
  end subroutine forces
  
  subroutine hessian(zero,box,pos,ids,rad,neighbors,number_neighbors,hes)
    logical,          intent(in)    :: zero ! to set variables to zero
    double precision, intent(in)    :: box(:)
    double precision, intent(in)    :: pos(:,:)
    integer,          intent(in)    :: ids(:)
    double precision, intent(in)    :: rad(:)  ! not used here
    integer,          intent(in)    :: neighbors(:,:), number_neighbors(:)
    !double precision, intent(inout) :: hes(size(pos,1),size(pos,2),size(pos,1),size(pos,2))
    double precision, intent(inout) :: hes(:,:,:,:)
    double precision                :: rij(size(pos,1)), rijsq, uij, wij, wwij, hbox(size(pos,1))
    double precision                :: unity(size(pos,1),size(pos,1)), mij(size(pos,1),size(pos,1)), mmij(size(pos,1),size(pos,1))
    integer                         :: i, j, isp, jsp, jn
    logical                         :: zero_ij
    if (zero) hes = 0.0d0
    unity = 0.0d0
    hbox = box / 2
    do i = 1,size(unity,1)
       unity(i,i) = 1.0d0
    end do
    loop_i: do i = 1,size(pos,2)
       isp = ids(i)
       loop_j: do jn = 1,number_neighbors(i)
          j = neighbors(jn,i)
          jsp = ids(j)
          rij = pos(:,i) - pos(:,j)
          call pbc(rij,box,hbox)
          call dot(rij,rij,rijsq)
          rijsq = rijsq / (rad(i)+rad(j))**2
          call is_zero(isp,jsp,rijsq,zero_ij)
          if (.not.zero_ij) then
             call compute(isp,jsp,rijsq,uij,wij,wwij)
             call smooth(isp,jsp,rijsq,uij,wij,wwij)
             wij = wij / (rad(i)+rad(j))**2
             wwij = wwij / (rad(i)+rad(j))**4
             mij = unity(:,:) * wij
             mmij = outer_product(rij,rij) * wwij
             ! Diagonal in i,j - diagonal in x,y
             hes(:,i,:,i) = hes(:,i,:,i) - mij
             hes(:,j,:,j) = hes(:,j,:,j) - mij
             ! Off-diagonal in i,j - diagonal in x,y
             hes(:,i,:,j) = hes(:,i,:,j) + mij
             hes(:,j,:,i) = hes(:,j,:,i) + mij
             ! Diagonal in i,j - off-diagonal in x,y
             hes(:,i,:,i) = hes(:,i,:,i) + mmij
             hes(:,j,:,j) = hes(:,j,:,j) + mmij
             ! Off-diagonal in i,j - off-diagonal in x,y
             hes(:,i,:,j) = hes(:,i,:,j) - mmij
             hes(:,j,:,i) = hes(:,j,:,i) - mmij
          end if
       end do loop_j
    end do loop_i
  end subroutine hessian

end module interaction_polydisperse_neighbors
