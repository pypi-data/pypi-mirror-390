 module neighbor_list

  ! use helpers
  
  implicit none

contains

  pure subroutine pbc(r,box,hbox)
    double precision, intent(inout) :: r(:)
    double precision, intent(in)    :: box(:), hbox(:)
    where (abs(r) > hbox)
       r = r - sign(box,r)
    end where
  end subroutine pbc

  pure subroutine distance(i,j,pos,rij)
    integer, intent(in) :: i, j
    double precision, intent(in)    :: pos(:,:)
    double precision, intent(inout) :: rij(:)
    rij = pos(:,i) - pos(:,j)
  end subroutine distance

  pure subroutine dot(r1,r2,out)
    double precision, intent(in)  :: r1(:), r2(:)
    double precision, intent(out) :: out
    out = dot_product(r1,r2)
  end subroutine dot

  subroutine zero(x)
    double precision, intent(inout)  :: x(:,:)
    !$omp parallel workshare
    x = 0.d0
    !$omp end parallel workshare
  end subroutine zero

  subroutine compute(box,pos,ids,rcut,neighbors,number_neighbors,distances,error)
    !! Compute neighbor lists using III Newton law
    double precision, intent(in)    :: box(:)
    double precision, intent(in)    :: pos(:,:), rcut(:,:)
    integer,          intent(in)    :: ids(:)
    integer,          intent(inout) :: neighbors(:,:), number_neighbors(size(pos,2))
    double precision, intent(inout) :: distances(size(neighbors,1), size(neighbors,2))
    logical,          intent(out)   :: error
    double precision                :: rij(size(pos,1)), rijsq, hbox(size(pos,1))
    integer                         :: i, j, isp, jsp
    error = .false.
    hbox = box / 2
    !$omp parallel default(private) firstprivate(rcut) shared(pos,ids,box,hbox,neighbors,number_neighbors,distances,error)
    !$omp do schedule(runtime)
    do i = 1,size(pos,2)
       number_neighbors(i) = 0
       isp = ids(i)
       do j = i+1,size(pos,2)
          jsp = ids(j)
          call distance(i,j,pos,rij)
          call pbc(rij,box,hbox)
          call dot(rij,rij,rijsq)
          if (rijsq <= rcut(isp,jsp)**2) then
             number_neighbors(i) = number_neighbors(i) + 1
             if (number_neighbors(i) <= size(neighbors,1)) then
                neighbors(number_neighbors(i),i) = j
                distances(number_neighbors(i),i) = rijsq
             else
                error = .true.
             end if
          end if
       end do
    end do
    !$omp end parallel
  end subroutine compute

  subroutine compute_from_neighbors(box,pos,ids,rcut,inp_neighbors,inp_number_neighbors,neighbors,number_neighbors,distances,error)
    !! Compute neighbor lists using III Newton law
    double precision, intent(in)    :: box(:)
    double precision, intent(in)    :: pos(:,:), rcut(:,:)
    integer,          intent(in)    :: ids(:)
    integer,          intent(in)    :: inp_neighbors(:,:), inp_number_neighbors(size(pos,2))
    integer,          intent(inout) :: neighbors(:,:), number_neighbors(size(pos,2))
    double precision, intent(inout) :: distances(size(neighbors,1), size(neighbors,2))
    logical,          intent(out)   :: error
    double precision                :: rij(size(pos,1)), rijsq, hbox(size(pos,1))
    integer                         :: i, j, jn, isp, jsp
    error = .false.
    hbox = box / 2
    !$omp parallel default(private) firstprivate(rcut) shared(pos,ids,box,hbox,neighbors,number_neighbors,distances,error)
    !$omp do schedule(runtime)
    do i = 1,size(pos,2)
       number_neighbors(i) = 0
       isp = ids(i)
       do jn = 1,inp_number_neighbors(i)
          j = inp_neighbors(jn,i)
          jsp = ids(j)
          call distance(i,j,pos,rij)
          call pbc(rij,box,hbox)
          call dot(rij,rij,rijsq)
          if (rijsq <= rcut(isp,jsp)**2) then
             number_neighbors(i) = number_neighbors(i) + 1
             if (number_neighbors(i) <= size(neighbors,1)) then
                neighbors(number_neighbors(i),i) = j
                distances(number_neighbors(i),i) = rijsq
             else
                error = .true.
             end if
          end if
       end do
    end do
    !$omp end parallel
  end subroutine compute_from_neighbors
  
  subroutine compute_full(box,pos,ids,rcut,neighbors,number_neighbors,distances,error)
    !! Compute full neighbor lists without assuming III Newton law will be used
    double precision, intent(in)    :: box(:)
    double precision, intent(in)    :: pos(:,:), rcut(:,:)
    integer,          intent(in)    :: ids(:)
    integer,          intent(inout) :: neighbors(:,:), number_neighbors(size(pos,2))
    double precision, intent(inout) :: distances(size(neighbors,1), size(neighbors,2))
    logical,          intent(out)   :: error
    double precision                :: rij(size(pos,1)), rijsq, hbox(size(pos,1))
    integer                         :: i, j, isp, jsp
    error = .false.
    hbox = box / 2
    number_neighbors(:) = 0
    ! TODO: add openmp parallel
    do i = 1,size(pos,2)
       isp = ids(i)
       do j = i+1,size(pos,2)
          if (i==j) cycle
          jsp = ids(j)
          call distance(i,j,pos,rij)
          call pbc(rij,box,hbox)
          call dot(rij,rij,rijsq)
          if (rijsq <= rcut(isp,jsp)**2) then
             number_neighbors(i) = number_neighbors(i) + 1
             number_neighbors(j) = number_neighbors(j) + 1
             if (number_neighbors(i) <= size(neighbors,1)) then
                neighbors(number_neighbors(i),i) = j
                distances(number_neighbors(i),i) = rijsq
             else
                error = .true.
             end if
             if (number_neighbors(j) <= size(neighbors,1)) then
                neighbors(number_neighbors(j),j) = i
                distances(number_neighbors(j),j) = rijsq
             else
                error = .true.
             end if
          end if
       end do
    end do
  end subroutine compute_full

  ! Solid-angle nearest neighbors (SANN), cf. van Meel, Filion, Valeriani and Frenkel (2011)
  ! Adapted from partycls, by Joris Paret
  SUBROUTINE compute_sann(box, pos, ids, rcutoff, neighbors, number_neighbors, distances, error)
    ! Parameters
    REAL(8), INTENT(in)     :: pos(:,:) ! position of i and all other particles
    REAL(8), INTENT(in)     :: rcutoff ! cutoff distance to identify all potential neighbours 
    REAL(8), INTENT(in)     :: box(:) ! edge of the simulation box  
    INTEGER :: ids(:)
    !INTEGER(8), INTENT(out) :: selectedneighbors(500) ! list of selected neighbours in group = 1
    integer,  intent(inout) :: neighbors(:,:), number_neighbors(size(pos,2))
    real(8), intent(inout) :: distances(size(neighbors,1), size(neighbors,2))
    logical,          intent(out)   :: error
    ! Variables
    INTEGER :: i, j, k, m ! m = tentative number of neighbours
    INTEGER :: np ! total number of particles, particles in group=1
    INTEGER :: countneighbors ! countneighbors = number of neighbours of particle i
    INTEGER :: neighbor(500) ! list of neighbours of particles i
    INTEGER :: sortneighbor(500) ! sorted 
    INTEGER :: Nb ! final number of neighbours of particle i
    INTEGER :: idx_j ! index of particle j
    REAL(8)    :: distance(500) ! distance = list of distances between each 
    REAL(8)    :: distancesorted(500) ! distancesorted = sorted distances       
    REAL(8)    :: rm, rm1 ! R(m) as in Eq.3 in the manuscript
    REAL(8)    :: r_ij(SIZE(box)) ! vector between i and j
    REAL(8)    :: rcutoff_sq, d_ij ! distance between particle i and particle j
    ! Computation
    error = .false.
    rcutoff_sq = rcutoff**2
    DO i = 1,SIZE(pos, 2)
       countneighbors = 0
       ! *** STEP 1 ***
       ! first we identify the particles within a cutoff radius rcutoff
       ! loop over all particles different from i
       DO j = 1,SIZE(pos, 2)
          IF (i == j) cycle
          r_ij(:) =  pos(:,j) - pos(:,i)
          CALL pbc(r_ij, box, box/2)
          d_ij = SUM(r_ij**2)
          ! identify neighbours that are within a cutoff (rcutoff)
          IF (d_ij < rcutoff_sq) THEN
             ! j is a neighbour of i
             countneighbors = countneighbors + 1
             ! build a list of neighbours
             neighbor(countneighbors) = j 
             ! create a list with the distance between i and j 
             distance(countneighbors) = d_ij
          END IF
       END DO

       ! *** STEP 2 ***
       ! sort all (countneighbors)
       ! neighbours (neighbor) according to their 
       ! distances (distance) and create  a new list of 
       ! particle i's (sortneighbor)
       ! and a new sorted list of distances (distancesorted)
       m = countneighbors
       !CALL insertion_sort_inplace(neighbor(1:m), distance(1:m))  !, sortneighbor(1:m), distancesorted(1:m))
       !sortneighbor(1:m) = neighbor(1:m)
       !distancesorted(1:m) = distance(1:m)
       CALL insertion_sort(neighbor(1:m), distance(1:m), sortneighbor(1:m), distancesorted(1:m))
       !do k=1,m
       !   if (i==1) print*, k, sortneighbor(k), distancesorted(k)
       !end do
       ! *** STEP 3 *** 
       ! start with 3 neighbours
       m = 3
       ! *** STEP 4 ***
       ! compute R(m) as in Eq.3 
       rm = 0
       DO k=1,m
          rm = rm + distancesorted(k)
       END DO
       rm = rm/(m-2)
       ! compute r(m+1)
       ! coslo: this fixes the issue that m can get larger than number of neighbors (by 2 units)
       !DO j = 1,countneighbors
       DO j = 1,countneighbors-3
          rm1 = 0
          DO k=1,m
             rm1 = rm1 + distancesorted(k)
          END DO
          rm1 = rm1/(m-2)
          ! *** STEP 5 ***  
          ! if rm > rm1     
          IF (rm >= rm1) THEN     
             rm = rm1
             ! increase m
             m = m+1
          ELSE
             ! *** STEP 6 ***
             ! if rm < rm1, m is the final number of neighbours
             ! coslo: this fixes an issue with SANN when the potential list is larger than m
             m = m - 1
             EXIT
          END IF
       END DO
       ! the final number of neighbours is m = Nb(i) 
       ! and the neighbours are  selectedneighbors
       number_neighbors(i) = m
       if (m <= size(neighbors, 1)) then
          neighbors(1:m, i) = sortneighbor(1:m)
          distances(1:m, i) = distancesorted(1:m)
          !do k = 1,m
          !   if(i==1) print*, k, neighbors(k,i), distancesorted(k), '*'
          !end do
       else
          error = .true.
       end if
    END DO
  END SUBROUTINE compute_sann

 subroutine insertion_sort(n, x, ns, xs)
    implicit none
    integer, intent(inout) :: n(:)
    real(8), intent(inout) :: x(:)
    integer, intent(out) :: ns(size(n))
    real(8), intent(out) :: xs(size(n))
    integer :: i,j
    integer :: temp
    real(8) :: temp_x
    ns = n
    xs = x
    do i=2,size(ns)
       temp=ns(i)
       temp_x=xs(i)
       do j=i-1,1,-1
          if (xs(j) <= temp_x) exit
          ns(j+1)=ns(j)
          xs(j+1)=xs(j)
       enddo
       ns(j+1)=temp
       xs(j+1)=temp_x
    enddo
  end subroutine insertion_sort

 subroutine insertion_sort_inplace(n, x)
    implicit none
    integer, intent(inout) :: n(:)
    real(8), intent(inout) :: x(:)
    integer :: i,j
    integer :: temp
    real(8) :: temp_x
    do i=2,size(n)
       temp=n(i)
       temp_x=x(i)
       do j=i-1,1,-1
          if (x(j) <= temp_x) exit
          n(j+1)=n(j)
          x(j+1)=x(j)
       enddo
       n(j+1)=temp
       x(j+1)=temp_x
    enddo
  end subroutine insertion_sort_inplace
  
  SUBROUTINE sort(neighbor, distance, sortneighbor, distancesorted)
    ! Parameters
    INTEGER, INTENT(inout) :: neighbor(:)
    REAL(8), INTENT(inout) :: distance(size(neighbor))
    INTEGER, INTENT(out) :: sortneighbor(size(neighbor))
    REAL(8), INTENT(out) :: distancesorted(size(neighbor))
    ! Variables
    INTEGER :: i, imin, j, n_tmp
    REAL(8)    :: d_tmp
    ! Computation
    DO i=1,size(neighbor)
      imin = i
      DO j=i+1,size(neighbor)
        IF (distance(j) < distance(imin)) THEN
          imin = j
        END IF
        d_tmp = distance(i)
        n_tmp = neighbor(i)
        distance(i) = distance(imin)
        neighbor(i) = neighbor(imin)
        distance(imin) = d_tmp
        neighbor(imin) = n_tmp
        distancesorted(i) = distance(i)
        sortneighbor(i) = neighbor(i)
        ! print*, sortneighbor(1:i)
     END DO
     if (i == size(neighbor)) sortneighbor(i) = neighbor(i)
     if (i == size(neighbor)) distancesorted(i) = distance(i)
     !print*, 'sort', i, imin, neighbor(i), sortneighbor(i)
    END DO
  END SUBROUTINE   
  
  logical function need_update_largest(displacement, skin)
    !! Update is needed if the largest displacement exceeds 1/2
    !! of the Verlet skin (from Allen & Tildesley)
    real(8), intent(in) :: displacement(:,:), skin
    real(8) :: dr(size(displacement,2)), dr_max, dr_tmp
    integer ::i
    dr_max = 0.d0
    !$omp parallel do private(dr_tmp) schedule(static) reduction(max:dr_max)
    do i = 1,size(displacement,2)
       dr_tmp = dot_product(displacement(:,i),displacement(:,i))
       if (dr_tmp > dr_max) dr_max = dr_tmp
    end do
    need_update_largest = dr_max > (skin / 2)**2
  end function need_update_largest

  subroutine add_displacement(pos,pos_old,box,displacement)
    !! Add displacements of particles for a subset of particles specified by index.
    !! Assume that PBC has been applied, hence we need to refold them.
    real(8), intent(in)    :: pos(:,:)
    real(8), intent(inout) :: pos_old(:,:), displacement(:,:)
    real(8), intent(in)    :: box(:)
    real(8) :: hbox(size(box))
    integer :: i
    hbox = box / 2
    !$omp parallel do schedule(static)
    do i = 1,size(pos,2)
       displacement(:,i) = displacement(:,i) + pos(:,i) - pos_old(:,i)
       call pbc(displacement(:,i),box,hbox)
       pos_old(:,i) = pos(:,i)
    end do
  end subroutine add_displacement
  
end module neighbor_list

