module interaction_test
  use interaction, only: forces_inter => forces
  use bond_term, only: forces_intra => forces
contains
  subroutine forces(zero,box,pos,spe,mol,rad,bond,bond_type,for,epot,virial)
    logical,          intent(in)    :: zero ! to set variables to zero
    double precision, intent(in)    :: box(:), pos(:,:), rad(:)
    integer,          intent(in)    :: spe(:), bond(:,:), bond_type(:)
    integer,          intent(in)    :: mol(:)  ! molecule to which particle belongs
    double precision, intent(inout) :: for(:,:)
    double precision, intent(inout) :: epot, virial
    call forces_inter(zero,box,pos,spe,rad,mol,for,epot,virial)
    call forces_intra(.false.,box,pos,spe,mol,rad,bond,bond_type,for,epot,virial)
  end subroutine forces
end module interaction_test

